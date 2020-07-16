#!/usr/bin/env python3

# Copyright (c) 2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

import logging
from logging.handlers import RotatingFileHandler
from logging.config import dictConfig
import os
import sys
import appdirs
import getopt
#from PySide2.QtCore import QApplication
from PySide2.QtWidgets import *
from PySide2.QtGui import *

from snopf_manager import SnopfManager

def init_logging(path=None):
    global logFileHandler
    if not path:
        path = appdirs.user_log_dir('snopf-manager', 'snopf')
    if not os.path.exists(path):
        os.makedirs(path)
    log_file = os.path.join(path, 'snopf_log.log')
    logFileFormatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
    logFileHandler = RotatingFileHandler(log_file, maxBytes=10*1024, backupCount=5)
    logFileHandler.setFormatter(logFileFormatter)
    logFileHandler.setLevel(logging.INFO)
    logConsoleFormatter = logging.Formatter('%(name)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
    logConsoleHandler = logging.StreamHandler()
    logConsoleHandler.setFormatter(logConsoleFormatter)
    logConsoleHandler.setLevel(logging.INFO)
    
    logging.root.setLevel(logging.INFO)
    logging.root.addHandler(logFileHandler)
    logging.root.addHandler(logConsoleHandler)
    
if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], 'c:l:')
    config_file_dir = None
    log_file_dir = None
    for o, a in opts:
        if o == '-c':
            config_file_dir = a
        elif o == '-l':
            log_file_dir = a
    init_logging(log_file_dir)
    app = QApplication([])
    w = SnopfManager(config_file_dir)
    w.show()
    sys.exit(app.exec_())
