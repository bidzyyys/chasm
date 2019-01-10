"""Module with logger creator"""
import logging
import sys


def get_logger(name, level, stream=sys.stdout):
    """
    Create logger with friendly format
    :param name: name of the logger
    :param level: logging level
    :param stream: output stream
    :return: logger
    """
    handler = logging.StreamHandler(stream=stream)
    formatter = logging.Formatter('[%(asctime)s]:[%(levelname)s]:[%(name)s]: %(message)s')
    formatter.datefmt = '%Y-%m-%d %H:%M:%S'
    handler.setFormatter(formatter)
    logger = logging.getLogger(name=name)
    logger.addHandler(handler)
    logger.setLevel(level=level)
    return logger
