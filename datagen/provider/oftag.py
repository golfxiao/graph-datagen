from typing import Dict
from faker import Faker
from faker.providers import BaseProvider

from datagen import log
from datagen import utils
from datagen.model import *
from datagen.enums import *
from datagen.provider import sequence, reference


def argparse(argstr):
    if argstr:
        return (argstr,)
    else:
        raise Exception(
            f"Invalid argument, unexpected empty string of oftag rule args."
        )


class Provider(BaseProvider):
    """The Oftag Provider for srcVID and dstVID. Steps:
    - First, get the specified TAG node according to the oftag configuration.
    - Then the vid generation rule can be obtained from the TAG node configuration.
    - So that srcVID and dstVID can be generated for oftag just like generating original vid for the vertex.

    There are two vid generation rules for oftag:
    - mode=0 indicates incremental sequence value,
    - mode=1 indicates random value
    """

    __provider__ = "oftag_provider"

    def __init__(
        self,
        generator,
        nodes: Dict[NKey, NodeConfig],
    ):
        super().__init__(generator)
        self.seq_provider = sequence.Provider(generator)
        self.ref_provider = reference.Provider(generator)
        self.nodes = nodes
        self.fake = Faker()

    def oftag(self, tag: str, mode: int = ID_MODE_SEQUENCE):
        nkey = NKey(tag, SCHEMA_TYPE_VERTEX)
        node = self.nodes[nkey]
        if not node:
            raise Exception(f"Not found rule for key:{nkey}")
        if mode not in [ID_MODE_RANDOM, ID_MODE_SEQUENCE]:
            raise Exception(f"Expect mode of tag {tag} in [0,1], but got {mode}.")

        prop = node.schema.get_prop_rule(PROP_VID)
        if prop.rule == GENERATOR_REFERENCE:
            return self.__vid_from_reference(node, prop, mode)
        elif prop.rule == GENERATOR_ID:
            return self.__vid_from_id(prop, mode, node.schema.gen_num)

    def __vid_from_reference(self, node: NodeConfig, prop: PropConfig, mode: int):
        holders = utils.extract_placeholder(prop.rule_args["pattern"])
        if len(holders) == 0:
            raise Exception(
                f"Unexpected placeholders empty of reference rule for key: {node.nkey}."
            )
        if len(holders) > 1:
            raise Exception(f"Expected 1 placeholder but got {len(holders)}.")

        id_rule = node.schema.get_prop_rule(holders[0])
        if id_rule.rule != GENERATOR_ID:
            raise Exception(
                f"Expect gen_rule:id but got gen_rule:{id_rule.rule} for prop:{id_rule.name}"
            )

        id = self.__vid_from_id(id_rule, mode, node.schema.gen_num)
        return self.ref_provider.reference(
            prop.rule_args["pattern"], **{holders[0]: id}
        )

    def __vid_from_id(self, prop: PropConfig, mode: int, gen_num: int):
        prefix = prop.rule_args.get("prefix")
        min = int(prop.rule_args["start"])
        max = min + gen_num
        if mode == ID_MODE_RANDOM:
            id = self.fake.random_int(min=min, max=max)
        else:
            id = self.seq_provider.id(tag=prop.name, start=min, max=max)
        return f"{prefix}{id}" if prefix else id

    def _reset(self):
        self.seq_provider._reset()
        log.info("Reset state for oftag provider.")
