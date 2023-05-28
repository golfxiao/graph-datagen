#!/usr/bin/env python

import argparse
import time
import sys
import yaml
import threading

from typing import *
from datagen import log
from datagen.taskqueue import TaskQueue
from datagen.config import ConfigManager
from datagen.producer import ProducerWorker
from datagen.storage import StorageWorker


def start(config):
    start_time = time.time()

    cfgmgr = ConfigManager(config)
    tqueue = TaskQueue(cfgmgr)
    workers: List[threading.Thread] = []
    num_workers = cfgmgr.get_config(["clientSettings", "numWorkers"])

    for thread_id in range(num_workers):
        t1 = ProducerWorker(tqueue, cfgmgr, thread_id)
        t2 = StorageWorker(tqueue, thread_id)
        t1.start()
        t2.start()
        workers.append(t1)
        workers.append(t2)

    # Wait for all worker threads to finish running
    for t in workers:
        t.join()

    end_time = time.time()
    log.info(f"all tasks run over, take {end_time-start_time:.3f} seconds.")
    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate test data for nebula graph.")
    parser.add_argument(
        "--config", type=str, required=True, help="Path to the yaml configuration file."
    )
    args = parser.parse_args()
    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    log.init(config["log"]["path"], config["log"]["level"])
    log.info(f"platform: {sys.platform}, config: {config}")
    start(config)
