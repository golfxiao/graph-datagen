import pytest
import sys
import os
import yaml
from datagen import log
from datagen.model import NKey
from datagen.config import ConfigManager


@pytest.fixture(scope="module")
def logger():
    log.init("./target/log/test.log", "debug")


@pytest.fixture(scope="module")
def config(logger):
    with open("./config_snb.yaml", "r") as f:
        config = yaml.safe_load(f)
    config["clientSettings"]["queueSize"] = 5
    config["clientSettings"]["numWorkers"] = 5
    return config


def test_parse(config, logger):
    assert config is not None
    assert config["log"]["path"]
    assert config["graph"]
    log.debug("config.graph: %s" % config["graph"])


def test_parse_nodes(config):
    cfgmgr = ConfigManager(config)
    nodes = cfgmgr.get_nodes()
    assert config and nodes
    assert len(nodes) == 4

    for e in nodes:
        assert e.nkey
        assert e.schema
        assert e.output


def test_get_node(config):
    cfgmgr = ConfigManager(config)
    assert cfgmgr.get_config(["clientSettings", "queueSize"]) == 5
    assert cfgmgr.get_config(["clientSettings", "numWorkers"]) == 5

    node1 = cfgmgr.get_node(NKey("student", "vertex"))
    node2 = cfgmgr.get_node(NKey("course", "vertex"))
    node3 = cfgmgr.get_node(NKey("follow", "edge"))
    node4 = cfgmgr.get_node(NKey("choose", "edge"))

    assert node1 and node1.schema and node1.output
    assert node2 and node2.schema and node2.output
    assert node3 and node3.schema and node3.output
    assert node4 and node4.schema and node4.output

    nodes_map = cfgmgr.get_nodes_map()
    assert nodes_map.get(NKey("student", "vertex"))
    assert nodes_map.get(NKey("course", "vertex"))
    assert nodes_map.get(NKey("follow", "edge"))
    assert nodes_map.get(NKey("choose", "edge"))
