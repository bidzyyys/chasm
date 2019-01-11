"""Module with maintenance creator"""
import logging
import sys


class Logger:
    level = None

    def __init__(self, name, stream=sys.stdout):
        if not Logger.level:
            raise RuntimeError('Tried to obtain a logger, not having previously set the level')

        handler = logging.StreamHandler(stream=stream)
        formatter = logging.Formatter('[%(asctime)s]:[%(levelname)s]:[%(name)s]: %(message)s')
        formatter.datefmt = '%Y-%m-%d %H:%M:%S'
        handler.setFormatter(formatter)
        logger = logging.getLogger(name=name)
        logger.addHandler(handler)
        logger.setLevel(level=Logger.level)

        self._logger = logger

    def __getattribute__(self, item):
        return super().__getattribute__('_logger').__getattribute__(item)
