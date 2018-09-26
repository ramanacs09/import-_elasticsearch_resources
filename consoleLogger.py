from __future__ import print_function
import logging


class Logger():
    def __init__(self):
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setFormatter(
            logging.Formatter('[%(processName)s] [%(threadName)s] [%(name)s] :: '
                              '[%(asctime)s] :: [%(levelname)s] :: [%(message)s]'))
        self.log = None

    def createLogHandler(self, name):
        self.log = logging.getLogger(name)
        self.log.addHandler(self.stream_handler)
        self.log.setLevel(logging.INFO)
        self.log.propagate = False

    def print(self, *args, **kwargs):
        self.log.info(*args, **kwargs)