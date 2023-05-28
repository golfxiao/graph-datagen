from typing import List, Dict, NamedTuple
from dataclasses import dataclass


@dataclass
class Vertex:
    vid: str = ""
    props: Dict[str, any] = None


@dataclass
class Edge:
    srcVID: str = ""
    dstVID: str = ""
    rank: int = 0
    props: Dict[str, any] = None


@dataclass
class OutConfig:
    type: str  # Output type, such as csv.
    path: str  # Output disk path
    batch_size: int  # number of datas written in batch.
    with_header: bool  # whether the header needs to be written in the CSV file


@dataclass
class PropConfig:
    name: str  # Property name，pattern: [tag].[prop_name]
    type: str  # Property value，such as int, string
    rule: str  # Generation rules, such as range
    rule_args: dict  # the parameters required by the rules, uniformly convert it to the tuplet


@dataclass
class Schema:
    tags: list = None  # The tag name list in the node, there is only one tag by the edge, there may be multiple tags by the vertex
    type: str = ""  # Node type，vertex or edge
    gen_num: int = 0  # Number of nodes to generate
    prop_rules: List[PropConfig] = None  # Property list

    def get_prop_rule(self, name) -> PropConfig:
        """Support to access property in two naming formats: tag.name and name"""
        for item in self.prop_rules:
            if item.name == name:
                return item
            if "." in item.name and item.name.split(".")[1] == name:
                return item
        return None


# The unique key of the node
NKey = NamedTuple("NKey", name=str, type=str)


# Node configuration, a sub-node under graph configuration.
@dataclass
class NodeConfig:
    nkey: NKey  # The unique key of the node
    schema: Schema  # Node structure configuration
    output: OutConfig  # Node ourput configuration


@dataclass
class GTask:
    """Task definition of generating data, currently a node corresponds to a task"""

    nkey: NKey  # The unique key of the node
    schema: Schema  # Node structure and generation rules configuration
    batch_size: int  # Number of datas generated in batch


@dataclass
class STask:
    """Task definition of storage data, a node will store data in multiple batches,
    each batch will generate a separate storage task alone."""

    nkey: NKey  # The unqiue key of the node
    output: OutConfig  # Node ourput configuration
    schema: Schema  # Node structure and generation rules configuration
    start_index: int  # The start index of the current data batch in total data set
    datalist: List  # The dataset of current data batch

    def __str__(self):
        return f"{self.nkey}, len: {len(self.datalist)}, row_idx: {self.start_index}"
