from builtins import eval as std_eval

from datagen.model import *
from datagen.enums import *
from datagen.provider import *
from datagen.mocker import DataMocker
from datagen import log


class ConfigManager:
    """General configuration and graph structure configuration management."""

    def __init__(self, config: dict):
        self.__config = config
        self.__test_mocker = DataMocker()
        self.__nodes = self.__parse_nodes(config)
        self.__nodes_map = self.__build_node_map(self.__nodes)

    def __build_node_map(self, nodes: List[NodeConfig]):
        m = {}
        for node in nodes:
            for tag in node.schema.tags:
                m[NKey(tag, node.schema.type)] = node
        return m

    def get_config(self, paths: list):
        """Gets a configuration item based on the configuration's hierarchical path.
        :param paths: yaml tree path where the configuration item resides. e.g. `clientSettings->locale` can be expressed as `['clientSettings','locale']`
        """
        if len(paths) == 0:
            return None
        config = self.__config
        for i, item in enumerate(paths):
            if not config[item]:
                return None
            if i == len(paths) - 1:
                return config[item]
            config = config[item]

        return None

    def get_node(self, nkey) -> NodeConfig:
        if nkey in self.__nodes_map:
            return self.__nodes_map[nkey]
        else:
            return None

    def get_nodes(self) -> List[NodeConfig]:
        return self.__nodes

    def get_nodes_map(self) -> Dict[NKey, NodeConfig]:
        return self.__nodes_map

    # ======================  Start parse the graph strucure configuration ===================
    def __parse_nodes(self, config):
        if not config:
            log.crit("invalid config empty.")
            return
        elements = config["graph"]
        nodes: list[NodeConfig] = []
        for e in elements:
            nodes.append(self.__parse_node(e))
        # TODO Checking and correcting error config: If there are multiple edges of the same name, we need to add _1, _2
        return nodes

    def __parse_node(self, c):
        """Parse node configuration, for multiple TAG cases in a Vertex, take the first TAG as
        the unique key for the node, and also support other TAG name to obtain node configuration.
        """
        output = self.__parse_output(c)
        obj = self.__parse_schema(c)
        key = NKey(obj.tags[0], obj.type)
        return NodeConfig(key, obj, output)

    def __parse_output(self, c: dict):
        c = c["output"]
        cfg = OutConfig(
            type=c["type"],
            path=c["path"],
            batch_size=c["batchSize"],
            with_header=c["csv"]["withHeader"],
        )
        return cfg

    def __parse_schema(self, c):
        type = c["schema"]["type"]
        schema = Schema(type=type)
        if type == SCHEMA_TYPE_VERTEX:
            schema.gen_num = int(c["schema"]["genNum"])
            schema.tags, schema.prop_rules = self.__parse_vertex(c["schema"]["vertex"])
        elif type == SCHEMA_TYPE_EDGE:
            schema.tags, schema.prop_rules = self.__parse_edge(c["schema"]["edge"])
        else:
            raise Exception(f"Unknown schema type of {type}")

        return schema

    def __parse_vertex(self, v):
        tags = []
        vtx_props: List[PropConfig] = []
        # When there are multiple tags in one vertex, all tag fields are placed in a list,
        # and the property name is formated as [tag].[Prop_name]
        for item in v["tags"]:
            tag_props = self.__parse_props(item["name"], item["props"])
            if not tag_props:
                raise Exception(f"Invalid props empty for tag:{item['name']}")
            tags.append(item["name"])
            vtx_props.extend(tag_props)

        vid_rule = self.__parse_required(v, "vid")
        vtx_props.append(vid_rule)
        return tags, vtx_props

    def __parse_edge(self, c):
        tag_name = c["name"]
        edge_props = self.__parse_props(tag_name, c["props"])
        src_vid_rule = self.__parse_required(c, PROP_SRC_VID)
        dst_vid_rule = self.__parse_required(c, PROP_DST_VID)
        gen_num_rule = self.__parse_required(c, PROP_EDGE_NUM_RULE)
        edge_props.append(src_vid_rule)
        edge_props.append(dst_vid_rule)
        edge_props.append(gen_num_rule)
        if PROP_RANK in c:
            rank_rule = self.__parse_required(c, PROP_RANK)
            edge_props.append(rank_rule)
        return [tag_name], edge_props

    def __parse_required(self, c: dict, name):
        """Parse the required field, and throw an error when it not exists."""
        if name not in c:
            raise Exception("Not found required prop {name}")
        if "genrule" not in c[name]:
            raise Exception("Not found required field:genrule for prop:{name}")

        rule, rule_args = self.__parse_rule(c[name]["genrule"])
        return PropConfig(name, c[name]["type"], rule, rule_args)

    def __parse_props(self, tag, props):
        if not props:
            return []

        nodes = []
        for p in props:
            prop_name = f"{tag}.{p['name']}"
            rule, rule_args = self.__parse_rule(p["genrule"])
            nodes.append(PropConfig(prop_name, p["type"], rule, rule_args))
        return nodes

    def __parse_rule(self, args):
        """Parse data generation rules and parameters"""
        if not args:
            raise Exception("Invalid genrule empty.")

        if type(args) != dict or not args["generator"]:
            raise Exception("Invalid genrule: generator empty.")

        rule_args = args.copy()
        rule = rule_args.pop("generator", None).strip()
        if len(rule) == 0:
            raise Exception("Invalid genrule: generator empty.")

        for k, v in rule_args.items():
            if k in COLLECTION_PARAMETERS:
                rule_args[k] = std_eval(v)
                log.info(f"Convert arg {k} to type:{type(rule_args[k])}")

        self.__test_mocker.check_rule(rule, rule_args)
        return rule, rule_args
