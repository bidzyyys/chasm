# pylint: disable=missing-docstring, too-many-arguments

from os import makedirs
from os.path import isdir
from shutil import rmtree

import pytest

from chasm.rpc import PAYLOAD_TAGS, PARAMS, METHOD
from chasm.rpc.client import run, get_account_data, \
    get_priv_key, create_account
from chasm.serialization.rlp_serializer import RLPSerializer

TEST_NODE = "127.0.0.1"
TEST_PORT = 6000

SAMPLE_ADDR = "3056301006072a8648ce3d020106052b8104000a0342000403526e777d17ae58b4a3db028dfdffd92f7c03f996fbfa238a215289e81fe0994ffeaae0ae6b01bff1b508dd9af7886314ebd743ccaf506a28f05677127c5890"
SAMPLE_PASSWORD = "test1234test1234"
TEST_DATADIR = "datadir"

rlp_serializer = RLPSerializer()


def skip_test():
    return pytest.mark.skipif(condition=check_server() is False,
                              reason="requires server running on {}:{}"
                              .format(TEST_NODE, TEST_PORT))


def check_server(port=TEST_PORT, node=TEST_NODE):
    payload = PAYLOAD_TAGS.copy()
    payload[METHOD] = "hello"
    payload[PARAMS] = []

    try:
        response = run(host=node, port=port,
                       payload=payload)
    except Exception:
        return False

    return response == 'elho'


def remove_dir(dir):
    rmtree(path=dir, ignore_errors=True)
    assert isdir(dir) is False


def create_dir_structure(path):
    makedirs(path, exist_ok=True)


def get_private_key(address, datadir, password):
    account = get_account_data(datadir=datadir,
                               pub_key_hex=address)
    priv_key = get_priv_key(account=account,
                            pwd=password)
    return priv_key


def mock_input_yes(s):
    return "yes"


def get_test_account(balance, utxos, dutxos_sum=0, dutxos=0, datadir=TEST_DATADIR, pwd=SAMPLE_PASSWORD):
    assert isdir(datadir) is False
    address, _ = create_account(datadir=datadir, pwd=pwd)
    init_address(address=address, balance=balance, utxos=utxos,
                 dutxos_sum=dutxos_sum, dutxos=dutxos)
    return {
        "address": address.hex(),
    }


def init_address(address, balance=0, utxos=0, dutxos_sum=0, dutxos=0):
    pass
