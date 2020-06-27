#!/usr/bin/env python3

# Copyright (c) 2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

import logging
from logging.handlers import RotatingFileHandler

logFileFormatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
logFileHandler = RotatingFileHandler('snopf_log.log', maxBytes=10*1024, backupCount=5)
logFileHandler.setFormatter(logFileFormatter)
logFileHandler.setLevel(logging.INFO)

logConsoleFormatter = logging.Formatter('%(name)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
logConsoleHandler = logging.StreamHandler()
logConsoleHandler.setFormatter(logConsoleFormatter)
logConsoleHandler.setLevel(logging.INFO)

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(logFileHandler)
    logger.addHandler(logConsoleHandler)
    return logger
