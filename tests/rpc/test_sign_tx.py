# pylint: disable=missing-docstring

from hashlib import sha3_256

from pytest_bdd import scenario, given, when, then, parsers
from ecdsa import VerifyingKey

from chasm.consensus import CURVE
from chasm.rpc import client
from chasm.rpc.client import sign_tx
from . import mock_acceptance


@scenario('test_sign_tx.feature', 'Sign given transaction')
def test_sign_tx():
    pass


@given(parsers.parse('Hex of the transaction'))
def parameters(transfer_transaction, rlp_serializer):
    return {
        "tx": rlp_serializer.encode(transfer_transaction).hex()
    }


@when('Alice signs the transaction')
def sign(parameters, alice_account, datadir):
    signing_key, address = alice_account

    client.input = mock_acceptance

    signature = sign_tx(tx_hex=parameters["tx"],
                        pub_key=address,
                        datadir=datadir,
                        signing_key=signing_key)

    parameters["signature"] = signature.hex()


@then('Signature is valid')
def verify_signature(parameters, alice_account):
    _, address = alice_account
    assert VerifyingKey.from_string(bytes.fromhex(address), curve=CURVE) \
        .verify(bytes.fromhex(parameters["signature"]),
                bytes.fromhex(parameters["tx"]),
                hashfunc=sha3_256)
