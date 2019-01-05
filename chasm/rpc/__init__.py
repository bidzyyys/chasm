"""RPC module"""

from chasm.consensus.xpeer_validation.tokens import Tokens
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

ALL_TOKENS = 0

TOKENS_DICT = {
    ALL_TOKENS: "all",
    Tokens.XPEER: "xpc",
    Tokens.BITCOIN: "btc",
    Tokens.ETHEREUM: "eth"
}


def token_from_name(name):
    for key in TOKENS_DICT:
        if TOKENS_DICT[key] == name.lower():
            return key

    raise ValueError("Token not found: %s", name)


def get_token_names():
    tokens = []
    for token in Tokens:
        tokens.append(TOKENS_DICT[token])

    return tokens


def list_token_names():
    tokens = str(get_token_names())
    tokens = tokens.replace("[", "")
    tokens = tokens.replace("]", "")

    return tokens


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
