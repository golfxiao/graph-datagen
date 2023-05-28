import threading
import time
import datetime

from datagen.model import *
from datagen.taskqueue import TaskQueue
from datagen.config import ConfigManager
from datagen.provider import *
from datagen.enums import *
from datagen.mocker import DataMocker
from datagen import log
from datagen import utils


class ProducerWorker(threading.Thread):
    """This thread is responsible for generating data. It continuously retrieves tasks
    from the generation queue and generates data in batches, which are then written to
    the storage queue. The thread will automatically exit when there are no more tasks to process.
    """

    def __init__(self, tqueue, cfgmgr, thread_id: int):
        super().__init__()
        self.__tqueue: TaskQueue = tqueue
        self.__cfgmgr: ConfigManager = cfgmgr
        self.__thread_id = thread_id
        self.__locale = self.__cfgmgr.get_config(["clientSettings", "locale"])
        self.__mocker: DataMocker = DataMocker(
            self.__locale, self.__cfgmgr.get_nodes_map()
        )

    def run(self):
        while True:
            task = self.__tqueue.pop_gtask()
            if not task:
                log.info(f"GTasks run over, gen-thread:{self.__thread_id} will exit.")
                self.__tqueue.push_stask(None, self.__thread_id)
                return

            start_time = time.time()
            self.__pre_execute(task)
            self.__execute(task)
            end_time = time.time()
            log.info(
                f"GTask end in thread:{self.__thread_id} take "
                f"{end_time-start_time:.3f} seconds, {task.nkey} "
            )

    def __pre_execute(self, task: GTask):
        """Do some necessary preprocessing work before running the task"""

        # Some provider have states, reset the state of the Mocker.
        self.__mocker.reset()

        # For edge types, the genNum of edge is determined by refering to the number of vertex which specified by oftag rule.
        if task.nkey.type == SCHEMA_TYPE_EDGE:
            task.schema.gen_num = self.__get_oftag_num(task)

        log.info(f"GTask start in thread:{self.__thread_id}, {task}")

    def __execute(self, task: GTask):
        """The main function of the task, generates all data of a node in batches according to batch_num configured,
        and push them into the stask_queue. Another worker will consume them.
        """
        buffer = []
        index = 0
        for _ in range(0, task.schema.gen_num):
            if task.nkey.type == SCHEMA_TYPE_VERTEX:
                buffer.append(self.__generate_vertex(task.schema))
            else:
                buffer.extend(self.__generate_edges(task.schema))

            if len(buffer) >= task.batch_size:
                log.debug(
                    f"A batch data({len(buffer)}) of {task.nkey} "
                    f"is queueing for storage, {index}/{task.schema.gen_num}"
                )
                self.__put_stask(task.nkey, buffer.copy(), index)
                index += len(buffer)
                buffer.clear()

        self.__put_stask(task.nkey, buffer.copy(), index)

    def __generate_vertex(self, schema: Schema) -> Vertex:
        """Generate a vertex object"""

        obj = Vertex(props={})

        for r in schema.prop_rules:
            val = self.__generate_prop(r, obj.props)
            if r.name == PROP_VID:
                obj.vid = val
            else:
                obj.props[r.name] = val

        return obj

    def __generate_edges(self, schema: Schema) -> List[Edge]:
        """Generate a single type of edge for a srcVID, and each srcVID may have multiple edges pointing to different dstVIDs.
        Steps:
        - First generate the srcVID
        - According to the user-configured rules, obtain the number of edges to be generated
        - Loop to generate multiple edges starting from srcVID according to edge_num_per_vid variable
        """
        edge_num_rule = schema.get_prop_rule(PROP_EDGE_NUM_RULE)
        edge_num_per_vid = self.__get_edge_num_per_vid(edge_num_rule)
        edges: List[Edge] = []

        base_vid_field = edge_num_rule.type
        vid = self.__generate_prop(schema.get_prop_rule(base_vid_field))

        for _ in range(edge_num_per_vid):
            item = Edge(props={})
            if base_vid_field == PROP_SRC_VID:
                item.srcVID = vid
            else:
                item.dstVID = vid

            for r in schema.prop_rules:
                if r.name in [base_vid_field, PROP_EDGE_NUM_RULE]:
                    continue
                val = self.__generate_prop(r, item.props)
                if r.name == PROP_DST_VID:
                    item.dstVID = val
                elif r.name == PROP_SRC_VID:
                    item.srcVID = val
                elif r.name == PROP_RANK:
                    item.rank = val
                else:
                    item.props[r.name] = val

            edges.append(item)

        return edges

    def __generate_prop(self, r: PropConfig, props=None):
        """Generate a property value"""
        rule_args = r.rule_args

        # The mock parameters of some custom providers requires special handling.
        if r.rule == GENERATOR_ID:
            # rule_args = (r.name, *(r.rule_args))
            rule_args["tag"] = r.name
        elif r.rule == GENERATOR_REFERENCE:
            # rule_args = (r.rule_args[0], utils.fix_dict_identifier(props))
            rule_args.update(utils.fix_dict_identifier(props))
        elif r.rule == GENERATOR_EVAL:
            # rule_args = (r.rule_args[0], utils.fix_dict_identifier(props))
            rule_args.update(utils.fix_dict_identifier(props))
        if r.rule == GENERATOR_OFTAG:
            mode = 0 if r.name == PROP_SRC_VID else 1
            rule_args["mode"] = mode
            # rule_args = (r.rule_args[0], mode)

        val = self.__mocker.mock(r.rule, rule_args)
        if r.type == VAL_TYPE_INT:
            if isinstance(val, datetime.datetime) or isinstance(val, datetime.date):
                return int(val.timestamp() * 1000)
            else:
                return int(val)
        elif r.type == VAL_TYPE_STRING:
            return str(val)
        elif r.type == VAL_TYPE_BOOL:
            return bool(val)
        elif r.type == VAL_TYPE_FLOAT:
            return float(val)
        else:
            return str(val)

    def __get_oftag_num(self, task: GTask) -> int:
        """Get the genNum of the vertex which is specified by oftag rule of srcVID"""
        src_rule = task.schema.get_prop_rule(PROP_SRC_VID)
        if not src_rule:
            raise Exception(f"Not found {PROP_SRC_VID} for schema: {task.nkey}")

        # oftag_nkey = NKey(src_rule.rule_args[0], SCHEMA_TYPE_VERTEX)
        oftag_nkey = NKey(src_rule.rule_args["tag"], SCHEMA_TYPE_VERTEX)
        oftag_rule = self.__cfgmgr.get_node(oftag_nkey)
        if not oftag_rule:
            raise Exception(f"Not found schema of vertex tag: {oftag_nkey}")

        return oftag_rule.schema.gen_num

    def __get_edge_num_per_vid(self, r: PropConfig) -> int:
        """The number of edges to be generated for each srcVID comes from user configuration,
        which may be configured as a fixed integer or a dynamic number range, and needs to be obtained using mock
        """
        if r.rule not in [GENERATOR_INT, GENERATOR_CONST]:
            raise Exception(f"Unsupported num_per_vid rule of edge: {r.name}")
        return int(self.__mocker.mock(r.rule, r.rule_args))

    def __put_stask(self, nkey: NKey, datalist: List, index: int):
        """After each batch of data is generated, it is stored in the stask queue specified by the thread_id"""
        node = self.__cfgmgr.get_node(nkey)
        if not node:
            raise Exception(f"Not found rule of tag: {nkey}")
        s_task = STask(nkey, node.output, node.schema, index, datalist)
        self.__tqueue.push_stask(s_task, self.__thread_id)
