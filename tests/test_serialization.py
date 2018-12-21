from pytest import fixture

from chasm import consensus
from chasm.primitives.transaction import Transaction, SignedTransaction
from chasm.primitives.tx_input import TxInput
from chasm.primitives.tx_output import TxTransferOutput, TxXpeerOutput
from chasm.serialization.serializer import Serializer


@fixture
def exchange():
    return consensus.HASH_FUNC(b'dead').digest()


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


@fixture
def transfer_transaction(tx_input, tx_transfer_output):
    return Transaction(inputs=[tx_input], outputs=[tx_transfer_output, tx_transfer_output])


@fixture
def signed_simple_transaction(alice, transfer_transaction):
    (priv_key, _pub) = alice
    signatures = [transfer_transaction.sign(priv_key)]
    return SignedTransaction(transfer_transaction, signatures)


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


def test_encode_transfer_transaction(transfer_transaction):
    encoded = Serializer.encode(transfer_transaction)
    decoded = Serializer.decode(encoded)
    assert decoded == transfer_transaction


def test_encode_signed_transaction(signed_simple_transaction):
    encoded = Serializer.encode(signed_simple_transaction)
    decoded = Serializer.decode(encoded)
    assert decoded == signed_simple_transaction
