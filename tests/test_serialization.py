import json

from merkletools import MerkleTools
from pytest import fixture, mark

from chasm import consensus
from chasm.consensus.primitives.block import Block
from chasm.consensus.primitives.transaction import Transaction, SignedTransaction, MintingTransaction, OfferTransaction, \
    MatchTransaction, ConfirmationTransaction, UnlockingDepositTransaction
from chasm.consensus.primitives.tx_input import TxInput
from chasm.consensus.primitives.tx_output import TransferOutput, XpeerOutput, XpeerFeeOutput
from chasm.consensus.xpeer_validation.tokens import Tokens
from chasm.serialization.json_serializer import JSONSerializer
from chasm.serialization.rlp_serializer import RLPSerializer


@fixture
def exchange():
    return consensus.HASH_FUNC(b'dead').digest()


@fixture
def tx_input():
    return TxInput(block_no=1, output_no=2)


@fixture
def tx_transfer_output(alice):
    (_priv_key, pub_key) = alice
    return TransferOutput(value=100, receiver=pub_key)


@fixture
def tx_transfer_outputs(tx_transfer_output):
    return [tx_transfer_output] * 10


@fixture
def tx_xpeer_output(alice, exchange):
    (_priv_key, pub_key) = alice
    return XpeerOutput(value=100, receiver=pub_key, exchange=exchange)


@fixture
def tx_xpeer_fee_output(exchange):
    return XpeerFeeOutput(100)


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
                            alice.pub, 0, 1, 0, 1000)


@fixture
def xpeer_match_transaction(xpeer_offer_transaction, tx_input, tx_transfer_outputs, bob):
    offer_hash = xpeer_offer_transaction.hash()
    return MatchTransaction([tx_input], tx_transfer_outputs, offer_hash, address_in=bob.pub)


@fixture
def xpeer_confirmation_transaction(xpeer_offer_transaction, tx_input, tx_transfer_outputs):
    offer_hash = xpeer_offer_transaction.hash()
    return ConfirmationTransaction([tx_input], tx_transfer_outputs, offer_hash, b'some proof', b'another proof')


@fixture
def xpeer_deposit_unlocking_transaction(xpeer_offer_transaction, tx_input, tx_transfer_outputs):
    offer_hash = xpeer_offer_transaction.hash()
    return UnlockingDepositTransaction([tx_input], tx_transfer_outputs, offer_hash, 0, b'some proof')


@fixture
def block(transfer_transaction, xpeer_offer_transaction, xpeer_deposit_unlocking_transaction, xpeer_match_transaction,
          xpeer_confirmation_transaction):
    transactions = [transfer_transaction, xpeer_offer_transaction, xpeer_deposit_unlocking_transaction,
                    xpeer_match_transaction, xpeer_confirmation_transaction]

    merkle_tree = MerkleTools(hash_type='sha256')
    merkle_tree.add_leaf(values=[tx.hash().hex() for tx in transactions])
    merkle_tree.make_tree()
    merkle_root = bytes.fromhex(merkle_tree.get_merkle_root())

    return Block(b'', merkle_root=merkle_root, difficulty=0, transactions=transactions)


@mark.parametrize('serializer', [RLPSerializer(), JSONSerializer()])
def test_encode_input(tx_input, serializer):
    encoded = serializer.encode(tx_input)
    decoded = serializer.decode(encoded)
    assert decoded == tx_input


@mark.parametrize('serializer', [RLPSerializer(), JSONSerializer()])
def test_encode_transfer_output(tx_transfer_output, serializer):
    encoded = serializer.encode(tx_transfer_output)
    decoded = serializer.decode(encoded)
    assert decoded == tx_transfer_output


@mark.parametrize('serializer', [RLPSerializer(), JSONSerializer()])
def test_encode_xpeer_output(tx_xpeer_output, serializer):
    encoded = serializer.encode(tx_xpeer_output)
    decoded = serializer.decode(encoded)
    assert decoded == tx_xpeer_output


@mark.parametrize('serializer', [RLPSerializer(), JSONSerializer()])
def test_encode_xpeer_fee_output(tx_xpeer_fee_output, serializer):
    encoded = serializer.encode(tx_xpeer_fee_output)
    decoded = serializer.decode(encoded)
    assert decoded == tx_xpeer_fee_output


@mark.parametrize('serializer', [RLPSerializer(), JSONSerializer()])
def test_encode_transfer_transaction(transfer_transaction, serializer):
    encoded = serializer.encode(transfer_transaction)
    decoded = serializer.decode(encoded)
    assert decoded == transfer_transaction


@mark.parametrize('serializer', [RLPSerializer(), JSONSerializer()])
def test_encode_signed_transaction(signed_simple_transaction, serializer):
    encoded = serializer.encode(signed_simple_transaction)
    decoded = serializer.decode(encoded)
    assert decoded == signed_simple_transaction


@mark.parametrize('serializer', [RLPSerializer(), JSONSerializer()])
def test_encode_minting_transaction(minting_transaction, serializer):
    encoded = serializer.encode(minting_transaction)
    decoded = serializer.decode(encoded)
    assert decoded == minting_transaction


@mark.parametrize('serializer', [RLPSerializer(), JSONSerializer()])
def test_encode_offer_transaction(xpeer_offer_transaction, serializer):
    encoded = serializer.encode(xpeer_offer_transaction)
    decoded = serializer.decode(encoded)
    assert decoded == xpeer_offer_transaction


@mark.parametrize('serializer', [RLPSerializer(), JSONSerializer()])
def test_encode_match_transaction(xpeer_match_transaction, serializer):
    encoded = serializer.encode(xpeer_match_transaction)
    decoded = serializer.decode(encoded)
    assert decoded == xpeer_match_transaction


@mark.parametrize('serializer', [RLPSerializer(), JSONSerializer()])
def test_encode_confirmation_transaction(xpeer_confirmation_transaction, serializer):
    encoded = serializer.encode(xpeer_confirmation_transaction)
    decoded = serializer.decode(encoded)
    assert decoded == xpeer_confirmation_transaction


@mark.parametrize('serializer', [RLPSerializer(), JSONSerializer()])
def test_encode_deposit_unlocking_transaction(xpeer_deposit_unlocking_transaction, serializer):
    encoded = serializer.encode(xpeer_deposit_unlocking_transaction)
    decoded = serializer.decode(encoded)
    assert decoded == xpeer_deposit_unlocking_transaction


@mark.parametrize('serializer', [RLPSerializer(), JSONSerializer()])
def test_encode_block(block, serializer):
    encoded = serializer.encode(block)
    decoded = serializer.decode(encoded)
    assert decoded == block
