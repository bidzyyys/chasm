import hashlib

from ecdsa import SigningKey, SECP256k1
from pytest import fixture

from chasm.primitives.transaction.tx_input import TxInput
from chasm.primitives.transaction.tx_output import TxTransferOutput, TxXpeerOutput
from chasm.serialization.serializer import Serializer


@fixture
def alice():
    sk = SigningKey.generate(curve=SECP256k1)
    return sk.to_string(), sk.get_verifying_key().to_string()


@fixture
def exchange():
    return hashlib.sha256(b'dead').digest()


@fixture
def tx_input():
    return TxInput(block_no=1, output_no=2)


@fixture
def tx_transfer_output(alice):
    (_priv_key, pub_key) = alice
    return TxTransferOutput(value=100, receiver=pub_key)


@fixture
def tx_xpeer_output(alice, exchange):
    (_priv_key, pub_key) = alice
    return TxXpeerOutput(value=100, receiver=pub_key, exchange=exchange)


def test_encode_input(tx_input):
    encoded = Serializer.encode(tx_input)
    decoded = Serializer.decode(encoded)
    assert decoded == tx_input


def test_encode_transfer_output(tx_transfer_output):
    encoded = Serializer.encode(tx_transfer_output)
    decoded = Serializer.decode(encoded)
    assert decoded == tx_transfer_output


def test_encode_xpeer_output(tx_xpeer_output):
    encoded = Serializer.encode(tx_xpeer_output)
    decoded = Serializer.decode(encoded)
    assert decoded == tx_xpeer_output
