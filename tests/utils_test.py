import os
import csv
import pytest

from datagen.utils import *
from datagen.model import *
from datagen import log


@pytest.fixture(scope="module")
def logger():
    log.init("./target/log/test.log", "debug")


def test_extract_placeholder():
    assert extract_placeholder("e_{event_id}") == ["event_id"]
    assert extract_placeholder("u_{user_id}") == ["user_id"]
    assert extract_placeholder("a_{user_id}") == ["user_id"]
    assert extract_placeholder("t_{ts_code}") == ["ts_code"]
    assert extract_placeholder("f_{industry_id}_{field_id}") == [
        "industry_id",
        "field_id",
    ]


def test_file_write():
    path = "./target/test/test.csv"
    mkdirs(path)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["hello", "world"])


def test_list(logger):
    # TODO List初始化的item都是同一个对象？
    edges = [Edge(props={})] * 10
    i = 0
    for i in range(0, 10):
        edges[i].srcVID = i
        edges[i].dstVID = i * 10
        edges[i].rank = i * 100
        edges[i].props["online_time"] = 3 * i
        edges[i].props["duration"] = 5 * i

    log.debug(f"edges: {edges}")


def test_fix_dict_identifier():
    map = {"user.user_id": 123, "user.name": "zhangsan"}
    fix_map = fix_dict_identifier(map)
    assert fix_map
    assert fix_map["user_id"] == map["user.user_id"]
    assert fix_map["name"] == map["user.name"]
