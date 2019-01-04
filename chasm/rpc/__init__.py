"""RPC module"""

from chasm.logger.logger import get_logger

# pylint: disable=invalid-name

logger = get_logger("chasm.rpc")

PWD_LEN = 32
ENCODING = "UTF-8"


class IncorrectPassword(ValueError):
    def __init__(self, message):
        super().__init__(message)


class InvalidAccountFile(ValueError):
    def __init__(self, message):
        super().__init__(message)
