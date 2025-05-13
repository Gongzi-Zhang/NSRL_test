'''
useful utilities
'''

import sys
import logging

class customFormatter(logging.Formatter):
    grey = "\x1b[30;20m"
    green = "\x1b[32;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    color = {
        logging.DEBUG: grey,
        logging.INFO: green,
        logging.WARNING: yellow,
        logging.ERROR: red,
        logging.CRITICAL: bold_red,
    }

    def __init__(self):
        self.FORMATS = {level: f'(%(filename)s:%(lineno)d) {self.color[level]} %(levelname)s{self.reset} - %(message)s' for level in self.color.keys()}

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

class _excludeErrorsFilter(logging.Filter):
    def filter(self, record):
        return record.levelno < logging.ERROR

logger = logging.getLogger()
logger.setLevel(logging.INFO)

h1 = logging.StreamHandler(sys.stdout)
h1.setLevel(logging.DEBUG)
h1.addFilter(lambda record: record.levelno <= logging.INFO)
h1.setFormatter(customFormatter())
h2 = logging.StreamHandler(sys.stderr)
h2.setLevel(logging.WARNING)
h2.setFormatter(customFormatter())

logger.addHandler(h1)
logger.addHandler(h2)
