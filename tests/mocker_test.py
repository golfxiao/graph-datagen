import pytest
import yaml
from datagen.config import ConfigManager
from datagen.mocker import *
from datagen.taskqueue import *
from datagen.provider import *
from datagen import log


@pytest.fixture(scope="module")
def logger():
    log.init("./target/log/test.log", "debug")


@pytest.fixture(scope="module")
def mocker(logger):
    with open("./examples/config_event.yaml", "r") as f:
        config = yaml.safe_load(f)
    cfgmgr = ConfigManager(config)
    mocker = DataMocker("zh-CN", cfgmgr.get_nodes_map())
    return mocker


def test_mock(mocker: DataMocker):
    name1 = mocker.mock(GENERATOR_NAME)
    name2 = mocker.mock(GENERATOR_NAME)
    name3 = mocker.mock(GENERATOR_NAME)
    name4 = mocker.mock(GENERATOR_NAME)
    assert name1 and name2 and name3 and name4
    log.debug(f"name: {name1}, {name2}, {name3}, {name4}")

    company1 = mocker.mock(GENERATOR_COMPANY)
    company2 = mocker.mock(GENERATOR_COMPANY)
    company3 = mocker.mock(GENERATOR_COMPANY)
    company4 = mocker.mock(GENERATOR_COMPANY)
    assert company1 and company2 and company3 and company4
    log.debug(f"company: {company1}, {company2}, {company3}, {company4}")

    sentence1 = mocker.mock(GENERATOR_SENTENCE, {"nb_words": 1})
    sentence2 = mocker.mock(GENERATOR_SENTENCE, {"nb_words": 4})
    sentence3 = mocker.mock(GENERATOR_SENTENCE, {"nb_words": 10})
    sentence4 = mocker.mock(GENERATOR_SENTENCE, {"nb_words": 50})
    assert sentence1 and sentence2 and sentence3 and sentence4
    log.debug(f"sentence: {sentence1}, {sentence2}, {sentence3}, {sentence4}")

    element1 = mocker.mock(GENERATOR_ELEMENT, {"elements": (1, 2, 3, 4)})
    element2 = mocker.mock(GENERATOR_ELEMENT, {"elements": (4.4, 5, 6.0)})
    element3 = mocker.mock(
        GENERATOR_ELEMENT, {"elements": ("zhangsan", "lisi", "wangwu", "zhaoliu")}
    )
    assert element1 and element2 and element3
    log.debug(f"element: {element1}, {element2}, {element3}")

    int1 = mocker.mock(GENERATOR_INT, {"min": 1, "max": 5})
    int2 = mocker.mock(GENERATOR_INT, {"min": 4, "max": 10})
    int3 = mocker.mock(GENERATOR_INT, {"min": 10, "max": 20})
    int4 = mocker.mock(GENERATOR_INT, {"min": 50, "max": 100})
    assert int1 and int2 and int3 and int4
    log.debug(f"int: {int1}, {int2}, {int3}, {int4}")

    number1 = mocker.mock(GENERATOR_NUMBER, {"digits": 2})
    number2 = mocker.mock(GENERATOR_NUMBER, {"digits": 4})
    number3 = mocker.mock(GENERATOR_NUMBER, {"digits": 8})
    number4 = mocker.mock(GENERATOR_NUMBER, {"digits": 50})
    assert number1 and number2 and number3 and number4
    log.debug(f"number: {number1}, {number2}, {number3}, {number4}")


def test_mock_reference(mocker: DataMocker):
    ref1 = mocker.mock(
        GENERATOR_REFERENCE, {"pattern": "e_{event_id}", "event_id": 3333}
    )
    ref2 = mocker.mock(
        GENERATOR_REFERENCE, {"pattern": "u_{user_id}", "user_id": 2382939}
    )
    ref3 = mocker.mock(
        GENERATOR_REFERENCE,
        {"pattern": "t_{ts_code}", "ts_code": "TS.239323"},
    )
    ref4 = mocker.mock(
        GENERATOR_REFERENCE, {"pattern": "a_{user_id}", "user_id": 444444}
    )
    assert ref1 and ref2 and ref3 and ref4
    log.debug(f"ref: {ref1}, {ref2}, {ref3}, {ref4}")

    eval1 = mocker.mock(
        GENERATOR_EVAL,
        {"expr": "start_time+duration", "start_time": 100, "duration": 5},
    )
    assert eval1
    log.debug(f"eval: {eval1}")


def test_mock_id(mocker: DataMocker):
    seq1 = mocker.mock(GENERATOR_ID, {"tag": "event", "start": 10, "max": 20})
    seq2 = mocker.mock(GENERATOR_ID, {"tag": "user", "start": 100})
    seq3 = mocker.mock(GENERATOR_ID, {"tag": "field", "start": 1000})
    seq4 = mocker.mock(GENERATOR_ID, {"tag": "audience", "start": 10000000})
    assert seq1 and seq2 and seq3 and seq4
    assert seq1 == 10 and seq2 == 100 and seq3 == 1000 and seq4 == 10000000
    log.debug(f"seq: {seq1}, {seq2}, {seq3}, {seq4}")

    seq5 = mocker.mock(GENERATOR_ID, {"tag": "topic", "start": 1000})
    seq6 = mocker.mock(GENERATOR_ID, {"tag": "topic", "start": 1000})
    seq7 = mocker.mock(GENERATOR_ID, {"tag": "topic", "start": 1000})
    assert seq5 == 1000 and seq6 == 1001 and seq7 == 1002
    mocker.reset()
    seq8 = mocker.mock(GENERATOR_ID, {"tag": "topic", "start": 1000})
    seq9 = mocker.mock(GENERATOR_ID, {"tag": "topic", "start": 1000})
    assert seq8 == 1000 and seq9 == 1001


def test_mock_oftag(mocker: DataMocker):
    oftag1 = mocker.mock(GENERATOR_OFTAG, {"tag": "field", "mode": ID_MODE_RANDOM})
    oftag2 = mocker.mock(GENERATOR_OFTAG, {"tag": "user", "mode": ID_MODE_RANDOM})
    assert oftag1 and oftag2
    log.debug(f"oftag: {oftag1}, {oftag2}")

    e1 = mocker.mock(GENERATOR_OFTAG, {"tag": "event", "mode": ID_MODE_SEQUENCE})
    e2 = mocker.mock(GENERATOR_OFTAG, {"tag": "event", "mode": ID_MODE_SEQUENCE})
    e3 = mocker.mock(GENERATOR_OFTAG, {"tag": "event", "mode": ID_MODE_SEQUENCE})
    e4 = mocker.mock(GENERATOR_OFTAG, {"tag": "event", "mode": ID_MODE_SEQUENCE})

    assert e1 < e2 < e3 < e4
    log.debug(f"oftag: {e1}, {e2}, {e3}, {e4}")

    mocker.reset()

    e5 = mocker.mock(GENERATOR_OFTAG, {"tag": "event", "mode": ID_MODE_SEQUENCE})
    e6 = mocker.mock(GENERATOR_OFTAG, {"tag": "event", "mode": ID_MODE_SEQUENCE})
    e7 = mocker.mock(GENERATOR_OFTAG, {"tag": "event", "mode": ID_MODE_SEQUENCE})
    e8 = mocker.mock(GENERATOR_OFTAG, {"tag": "event", "mode": ID_MODE_SEQUENCE})
    assert e5 == e1 and e6 == e2 and e7 == e3 and e8 == e4
