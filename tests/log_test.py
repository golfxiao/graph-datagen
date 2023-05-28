import pytest
import logging
from datagen import log


def test_log():
    # log.init("./target/log/test.log", "debug")
    log.init("console", "debug")
    log.debug("this is a debug log.")
    log.info("this is a info log.")
    log.warn("this is a warn log.")
    log.error("this is a error log.")
    log.crit("this is a critical log.")

    log.init("./target/log/test.log", "debug")
    log.debug("this is a debug log in file.")
    log.info("this is a info log in file.")
    log.warn("this is a warn log in file.")
    log.error("this is a error log in file.")
    log.crit("this is a critical log in file.")
