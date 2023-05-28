import os
import logging
from typing import Any
from datagen import utils


# Log level definition
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARN
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL


def init(log_path: str, log_level: str):
    global adapter
    handler: logging.Handler = None
    if log_path == "console":
        handler = logging.StreamHandler()
    else:
        utils.mkdirs(log_path)
        handler = logging.FileHandler(log_path, "a+")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))

    logger: logging.Logger = logging.getLogger(__name__)
    logger.setLevel(log_level.upper())
    logger.addHandler(handler)
    adapter = LineNumAdapter(logger, {})
    info(f"log config: {log_path}, {log_level}")


adapter: logging.LoggerAdapter = None

# Print log api definition
debug = lambda msg, *args, **kwargs: adapter.debug(msg, *args, **kwargs)
info = lambda msg, *args, **kwargs: adapter.info(msg, *args, **kwargs)
warn = lambda msg, *args, **kwargs: adapter.warning(msg, *args, **kwargs)
error = lambda msg, *args, **kwargs: adapter.error(msg, *args, **kwargs)
crit = lambda msg, *args, **kwargs: adapter.critical(msg, *args, **kwargs)


class LineNumAdapter(logging.LoggerAdapter):
    """Custom log adapter for printing the line number and filename"""

    def process(self, msg, kwargs):
        filename, lineno, _, _ = self.logger.findCaller(stacklevel=3)
        return f"[{os.path.basename(filename)}:{lineno}] {msg}", kwargs
