"""RPC module"""

from chasm.consensus.tokens import Tokens

# pylint: disable=invalid-name


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

ALL = 0
ALL_ADDRESSES = "0"

TOKENS_DICT = {
    ALL: "all",
    Tokens.XPEER: "xpc",
    Tokens.BITCOIN: "btc",
    Tokens.ETHEREUM: "eth"
}

TIMEOUT_FORMAT = "%Y-%m-%d::%H:%M:%S"


def get_token_name(token):
    return TOKENS_DICT.get(token, "Unknown: {}".format(token))


def token_from_name(name):
    for key in TOKENS_DICT:
        if TOKENS_DICT[key] == name.lower():
            if key is ALL:
                return key
            else:
                return key.value

    raise ValueError("Token not found: {}".format(name))


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
