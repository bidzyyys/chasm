# pylint: disable=missing-docstring

from hashlib import sha3_256
from os.path import isdir

from ecdsa import VerifyingKey
from pytest_bdd import scenario, given, when, then, parsers

from chasm.rpc import client
from chasm.rpc.client import sign_tx, create_account
from . import remove_dir, mock_input_yes, get_private_key


@scenario('test_sign_tx.feature', 'Sign given transaction')
def test_sign_tx():
    pass


@given(parsers.parse('New datadir: {datadir}, new address and hash of the transaction'))
def parameters(datadir):
    address, _ = create_account(datadir=datadir, pwd="test1234test1234")
    return {
        "datadir": datadir,
        "pwd": "test1234test1234",
        "address": address.hex(),
        "tx": "f8de04b8dbf8d9cc8bca8088c785546573747345f8cab862f86001b85df85b0ab8583056301006072a8648ce3d020106052b8104000a034200042a86469754777b30bc63304ac057db2882b1a69a81ac57b4dae3490f0df367d7232e81be05d5520742191a5d5254b0be544255ad4148fd7efb3667e58828e4d2b864f86201b85ff85d8203ddb8583056301006072a8648ce3d020106052b8104000a034200042a86469754777b30bc63304ac057db2882b1a69a81ac57b4dae3490f0df367d7232e81be05d5520742191a5d5254b0be544255ad4148fd7efb3667e58828e4d2"
    }


@when('I sign the transaction')
def sign(parameters):
    priv_key = get_private_key(datadir=parameters["datadir"],
                               address=parameters["address"],
                               password=parameters["pwd"])

    client.input = mock_input_yes

    signature = sign_tx(tx_hex=parameters["tx"],
                        pub_key=parameters["address"],
                        datadir=parameters["datadir"],
                        signing_key=priv_key)

    parameters["signature"] = signature.hex()


@then('Signature is valid')
def verify_signature(parameters):
    pub_key = VerifyingKey.from_der(bytes.fromhex(parameters["address"]))
    assert pub_key.verify(bytes.fromhex(parameters["signature"]),
                          bytes.fromhex(parameters["tx"]),
                          hashfunc=sha3_256)


@then('Datadir is removed')
def cleanup(parameters):
    remove_dir(parameters["datadir"])
    assert isdir(parameters["datadir"]) is False
