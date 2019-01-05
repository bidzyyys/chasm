"""RPC module"""

from chasm.logger.logger import get_logger

# pylint: disable=invalid-name

logger = get_logger("chasm.rpc")

PWD_LEN = 32
ENCODING = "UTF-8"
KEYSTORE = "keystore"
KEY_FILE_REGEX = r'[0-9]{8}_[0-9]{6}_[0-9|a-z|A-Z]{7}.json'

PAYLOAD_TAGS = {
    "jsonrpc": "2.0",
    "id": 0,
}

METHOD = "method"
PARAMS = "params"


class IncorrectPassword(ValueError):
    def __init__(self, message):
        super().__init__(message)


class InvalidAccountFile(ValueError):
    def __init__(self, message):
        super().__init__(message)


class RPCError(ValueError):
    def __init__(self, message):
        super().__init__(message)


class BadResponse(RPCError):
    def __init__(self, message):
        super().__init__(message)
