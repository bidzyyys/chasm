from pytest import fixture

from chasm import consensus
from chasm.consensus.primitives.transaction import Transaction, SignedTransaction, MintingTransaction, OfferTransaction
from chasm.consensus.primitives.tx_input import TxInput
from chasm.consensus.primitives.tx_output import TxTransferOutput, TxXpeerOutput
from chasm.consensus.xpeer_validation.tokens import Tokens
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
def tx_transfer_outputs(tx_transfer_output):
    return [tx_transfer_output] * 10


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
    return SignedTransaction.build_signed(transfer_transaction, [priv_key])


@fixture
def minting_transaction(tx_transfer_outputs):
    return MintingTransaction(tx_transfer_outputs)


@fixture
def xpeer_offer_transaction(tx_input, tx_transfer_outputs, alice):
    return OfferTransaction([tx_input], tx_transfer_outputs, Tokens.BITCOIN.value, Tokens.ETHEREUM.value, 10, 100,
                            alice.pub, 0, 1, 0, 1000 )


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


def test_encode_minting_transaction(minting_transaction):
    encoded = Serializer.encode(minting_transaction)
    decoded = Serializer.decode(encoded)
    assert decoded == minting_transaction


def test_encode_offer_transaction(xpeer_offer_transaction):
    encoded = Serializer.encode(xpeer_offer_transaction)
    decoded = Serializer.decode(encoded)
    assert decoded == xpeer_offer_transaction
