# pylint: disable=missing-docstring, too-many-arguments

import pytest

from chasm.maintenance.config import Config, DEFAULT_TEST_CONFIG
from chasm.rpc import PAYLOAD_TAGS, PARAMS, METHOD
from chasm.rpc.client import run

CONFIG = Config([DEFAULT_TEST_CONFIG])


def skip_test():
    return pytest.mark.skipif(condition=check_server() is False,
                              reason="requires server running on port: {}"
                              .format(CONFIG.rpc_port()))


def check_server(port=CONFIG.rpc_port(), node='localhost'):
    payload = PAYLOAD_TAGS.copy()
    payload[METHOD] = "hello"
    payload[PARAMS] = []

    try:
        response = run(host=node, port=port,
                       payload=payload)
    except Exception:
        return False

    return response == 'elho'


def mock_acceptance(s):
    return "yes"


def init_address(address, balance=0, utxos=0, dutxos_sum=0, dutxos=0):
    pass
