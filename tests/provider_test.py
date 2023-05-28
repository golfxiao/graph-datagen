import pytest
import yaml
from faker.generator import Generator
from datagen.config import ConfigManager
from datagen.provider import *
from datagen.taskqueue import TaskQueue


@pytest.fixture(scope="module")
def logger():
    log.init("./target/log/test.log", "debug")


@pytest.fixture(scope="module")
def nodes(logger):
    with open("./examples/config_event.yaml", "r") as f:
        config = yaml.safe_load(f)
    cfgmgr = ConfigManager(config)
    return cfgmgr.get_nodes_map()


def test_const():
    p = ConstProvider(Generator())
    assert p.const(10) == 10
    assert p.const("hello") == "hello"
    assert p.const(7.65) == 7.65
    assert p.const(True) == True


def test_reference():
    p = ReferenceProvider(Generator())
    assert p.reference("u_{user_id}", user_id=123) == "u_123"
    assert p.reference("a_{user_id}", user_id=389548) == "a_389548"
    assert p.reference("e_{event_id}", event_id=123456) == "e_123456"
    assert p.reference("t_{ts_code}", ts_code="TS.888888") == "t_TS.888888"
    assert p.reference("f_{field_id}", field_id=5555) == "f_5555"

    assert p.reference("u_{user_id}", **{"user_id": 123}) == "u_123"


def test_eval():
    p = EvalProvider(Generator())
    assert (
        p.eval("start_time+duration", start_time=16839390000, duration=3600)
        == 16839393600
    )


def test_sequence():
    p = SequenceProvider(Generator())
    assert p.id("event_id", 3, 5) == 3
    assert p.id("event_id", 3, 5) == 4
    assert p.id("event_id", 3, 5) == 3
    assert p.id("event_id", 3, 5) == 4

    assert p.id("user_id", 1000, 2000) == 1000
    assert p.id("user_id", 1000, 2000) == 1001


def test_oftag(nodes):
    p = OftagProvider(Generator(), nodes)
    vid1 = p.oftag("event", 0)
    vid2 = p.oftag("event", 0)
    vid3 = p.oftag("event", 0)
    vid4 = p.oftag("event", 0)
    print("oftag event id: {}, {}, {}, {}".format(vid1, vid2, vid3, vid4))

    vid5 = p.oftag("event", 1)
    vid6 = p.oftag("event", 1)
    vid7 = p.oftag("event", 1)
    vid8 = p.oftag("event", 1)
    print("oftag random: {}, {}, {}, {}".format(vid5, vid6, vid7, vid8))

    # vid9 = p.oftag("uniform", 0)
    # assert vid9 is None
