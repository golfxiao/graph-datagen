import threading
from queue import Queue
from typing import List
from datagen import log
from datagen.model import *
from datagen.config import ConfigManager


class TaskQueue:
    """Task queue management. There are two queues：
    - Generation Task Queue，used to manage gneration tasks，which will be created at one time according to the node configuration.
    - Storage Task queue，used to manage storage tasks，which will be created dynamically in the process of generating data
    """

    def __init__(self, cfgmgr: ConfigManager):
        self.__lock = threading.Lock()

        num_workers = cfgmgr.get_config(["clientSettings", "numWorkers"])
        queue_size = cfgmgr.get_config(["clientSettings", "queueSize"])

        self.__gtask_queue = self.__build_gtasks(cfgmgr.get_nodes())
        self.__stask_queue = [None] * num_workers
        for slot in range(num_workers):
            self.__stask_queue[slot] = Queue(maxsize=queue_size)

        log.info(
            f"gtask count: {len(self.__gtask_queue)}, workers: {num_workers}, "
            f"store queue_size:{queue_size}"
        )

    def __build_gtasks(self, nodes: List[NodeConfig]):
        """Create data generation tasks for all nodes according to the node rule configuration."""

        tasks: List[GTask] = []
        for n in nodes:
            tasks.append(GTask(n.nkey, n.schema, n.output.batch_size))

        return tasks

    def pop_gtask(self) -> GTask:
        """Take out a generation task from the queue."""

        with self.__lock:
            if len(self.__gtask_queue) > 0:
                return self.__gtask_queue.pop(0)
            else:
                return None

    def pop_stask(self, slot: int) -> STask:
        """Take out a storage task from the queue."""

        if slot >= len(self.__stask_queue):
            log.warn(
                f"pop failed for param of slot:{slot} out of the range 0-{len(self.__stask_queue)}."
            )
            return None
        return self.__stask_queue[slot].get()

    def push_stask(self, task: STask, slot: int):
        """Push a storage task into the queue."""

        if slot >= len(self.__stask_queue):
            log.warn(
                f"Push stask failed for param of slot:{slot} out of the range 0-{len(self.__stask_queue)}."
            )
            return None
        self.__stask_queue[slot].put(task)
        log.debug(f"Push stask:{task} in slot: {slot}")
