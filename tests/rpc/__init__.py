# pylint: disable=missing-docstring

from chasm.rpc import PAYLOAD_TAGS, PARAMS, METHOD
from chasm.rpc.client import run

TEST_NODE = "127.0.0.1"
TEST_PORT = 6000

SAMPLE_ADDR = "3056301006072a8648ce3d020106052b8104000a034\
                2000403526e777d17ae58b4a3db028dfdffd92f7c\
                03f996fbfa238a215289e81fe0994ffeaae0ae6b0\
                1bff1b508dd9af7886314ebd743ccaf506a28f056\
                77127c5890"


def check_server(port=TEST_PORT, node=TEST_NODE):
    payload = PAYLOAD_TAGS.copy()
    payload[METHOD] = "helo"
    payload[PARAMS] = []

    try:
        response = run(host=node, port=port,
                       payload=payload)
    except Exception:
        return False

    return response == 'elho'


def init_address(address, balance=0, utxos=0, dutxo=0):
    pass
