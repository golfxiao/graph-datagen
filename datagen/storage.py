import threading
import time
import csv

from datagen.enums import *
from datagen.model import *
from datagen import utils
from datagen import log
from datagen.taskqueue import TaskQueue


class StorageWorker(threading.Thread):
    """This thread is responsible for data storage. It retrieves tasks from the storage queue
    and executes them. If no task is available, the thread will exit."""

    def __init__(self, tqueue, thread_id: int):
        super().__init__()
        self.__tqueue: TaskQueue = tqueue
        self.__thread_id = thread_id
        self.pre_task: STask = None

    def run(self):
        while True:
            log.debug(f"Pop stask in thread:{self.__thread_id}...")
            task = self.__tqueue.pop_stask(self.__thread_id)
            if task is None:
                log.info(f"Stasks run over, store thread:{self.__thread_id} will exit.")
                return

            start_time = time.time()
            self.__pre_execute(task)
            self.__execute_task(task)
            end_time = time.time()
            log.debug(
                f"STask end in thread:{self.__thread_id} "
                f"take {end_time-start_time:.3f} seconds, {task} "
            )

    def __pre_execute(self, task: STask):
        if self.pre_task is None or self.pre_task.nkey != task.nkey:
            utils.mkdirs(task.output.path)
            self.pre_task = task
            log.info(
                f"Start file write at thread:{self.__thread_id}, {task.output.path}"
            )

    def __execute_task(self, task: STask):
        """Build the data in csv format and write it to file."""
        schema = task.schema
        rows: List[List[str]] = []

        for item in task.datalist:
            if schema.type == SCHEMA_TYPE_VERTEX:
                rows.append(self.__vertex_to_csv(item, schema))
            else:
                rows.append(self.__edge_to_csv(item, schema))

        # After testing, it was found that manually maintaining file handles with open/close
        # has little effect on shortening program runtime. The bottleneck of the program
        # should be in the data generation process.
        with open(task.output.path, "a+", newline="") as f:
            writer = csv.writer(f)
            if task.start_index == 0 and task.output.with_header:
                writer.writerow(self.__header_to_csv(schema))
            writer.writerows(rows)

    def __header_to_csv(self, schema: Schema) -> List[str]:
        res: List[str] = []
        if schema.type == SCHEMA_TYPE_VERTEX:
            vid_rule = schema.get_prop_rule(PROP_VID)
            res.append(f":VID({vid_rule.type})")
        else:
            src_vid_rule = schema.get_prop_rule(PROP_SRC_VID)
            dst_vid_rule = schema.get_prop_rule(PROP_DST_VID)
            res.append(f":SRC_VID({src_vid_rule.type})")
            res.append(f":DST_VID({dst_vid_rule.type})")
            res.append(f":RANK")

        for prop in schema.prop_rules:
            if prop.name in PREDEFINED_PROPS:
                continue
            res.append(f"{prop.name}:{prop.type}")
        return res

    def __edge_to_csv(self, item: Edge, schema: Schema) -> List[str]:
        res: List[str] = [item.srcVID, item.dstVID, item.rank]
        if item.props is None:
            log.warn(f"Unexpected props empty for item:{item}")
            return res

        for prule in schema.prop_rules:
            if prule.name not in item.props:  # filter out special fields from schema
                continue
            res.append(item.props[prule.name])
        return res

    def __vertex_to_csv(self, item: Vertex, schema: Schema) -> List[str]:
        res: List[str] = [item.vid]
        if item.props is None:
            log.error(f"Unexpected props empty for item:{item}")
            return res

        for prule in schema.prop_rules:
            if prule.name not in item.props:  # filter out special fields from schema
                continue
            res.append(item.props[prule.name])
        return res
