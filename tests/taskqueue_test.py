import pytest
import yaml

from datagen import log
from datagen.config import ConfigManager
from datagen.model import *
from datagen.taskqueue import TaskQueue


@pytest.fixture(scope="module")
def logger():
    log.init("./target/log/test.log", "debug")


@pytest.fixture(scope="module")
def cfgmgr(logger):
    with open("./examples/config_event.yaml", "r") as f:
        config = yaml.safe_load(f)
    config["clientSettings"]["queueSize"] = 5
    config["clientSettings"]["numWorkers"] = 5
    cfgmgr = ConfigManager(config)
    return cfgmgr


def test_taskqueue(cfgmgr):
    tqueue = TaskQueue(cfgmgr)

    task1 = tqueue.pop_gtask()
    task2 = tqueue.pop_gtask()
    task3 = tqueue.pop_gtask()
    task4 = tqueue.pop_gtask()

    assert task1 and task1.schema and task1.batch_size == 5000
    assert task2 and task2.schema and task2.batch_size == 5000
    assert task3 and task3.schema and task3.batch_size == 5000
    assert task4 and task4.schema and task4.batch_size == 5000

    log.debug(f"gtask1:{task1.__str__}")
    log.debug(f"gtask2:{task2.__str__}")
    log.debug(f"gtask3:{task3.__str__}")
    log.debug(f"gtask4:{task4.__str__}")

    node1 = cfgmgr.get_node(NKey("event", "vertex"))
    node2 = cfgmgr.get_node(NKey("audience", "vertex"))
    node3 = cfgmgr.get_node(NKey("follow_topic", "edge"))
    node4 = cfgmgr.get_node(NKey("view", "edge"))

    tqueue.push_stask(STask(node1.nkey, node1.output, node1.schema, 1000, []), 0)
    tqueue.push_stask(STask(node2.nkey, node2.output, node2.schema, 1000, []), 1)
    tqueue.push_stask(STask(node3.nkey, node3.output, node3.schema, 1000, []), 2)
    tqueue.push_stask(STask(node4.nkey, node4.output, node4.schema, 1000, []), 3)

    stask1 = tqueue.pop_stask(0)
    stask2 = tqueue.pop_stask(1)
    stask3 = tqueue.pop_stask(2)
    stask4 = tqueue.pop_stask(3)

    assert (
        stask1.nkey == node1.nkey
        and stask1.schema == node1.schema
        and stask1.output == node1.output
    )
    assert (
        stask2.nkey == node2.nkey
        and stask2.schema == node2.schema
        and stask2.output == node2.output
    )
    assert (
        stask3.nkey == node3.nkey
        and stask3.schema == node3.schema
        and stask3.output == node3.output
    )
    assert (
        stask4.nkey == node4.nkey
        and stask4.schema == node4.schema
        and stask4.output == node4.output
    )

    log.debug(f"stask1:{stask1.__str__}")
    log.debug(f"stask2:{stask2.__str__}")
    log.debug(f"stask3:{stask3.__str__}")
    log.debug(f"stask4:{stask4.__str__}")
