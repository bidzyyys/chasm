import pytest
from ecdsa import VerifyingKey, BadSignatureError
from pytest import fixture

from chasm import consensus
from chasm.maintenance.exceptions import InputOutputSumsException
from chasm.consensus.primitives.transaction import Transaction, SignedTransaction
from chasm.consensus.primitives.tx_input import TxInput
from chasm.consensus.primitives.tx_output import TransferOutput
from chasm.serialization.rlp_serializer import RLPSerializer


@fixture
def inputs():
    return [TxInput(1, 1), TxInput(10, 100), TxInput(2, 1)]


@fixture
def utxos(inputs, alice, bob, carol):
    return [TransferOutput(100, entity.pub) for entity in [alice, bob, carol]]


@fixture
def transfer_outputs(alice, bob):
    return [TransferOutput(100, alice.pub), TransferOutput(10, bob.pub)]


@fixture
def simple_transaction(inputs, transfer_outputs, utxos):
    tx = Transaction(inputs, transfer_outputs)
    tx.utxos = utxos
    return tx


@fixture
def signed_simple_transaction(simple_transaction, alice, bob, carol):
    return SignedTransaction.build_signed(simple_transaction, [alice, bob, carol])


def test_sign_transaction_and_manually_verify_signature(simple_transaction, alice, bob):
    entities = [alice, bob]
    for entity in entities:
        signature = simple_transaction.sign(entity.priv)
        vk = VerifyingKey.from_string(entity.pub, curve=consensus.CURVE)
        encoded = RLPSerializer().encode(simple_transaction)
        assert vk.verify(signature, encoded, consensus.HASH_FUNC)


def test_sign_and_verify_signature(simple_transaction, alice, bob):
    entities = [alice, bob]
    for entity in entities:
        assert simple_transaction.verify_signature(entity.pub, simple_transaction.sign(entity.priv))


def test_verifies_invalid_signature(simple_transaction, alice, bob):
    with pytest.raises(BadSignatureError):
        simple_transaction.verify_signature(alice.pub, simple_transaction.sign(bob.priv))


def test_verifies_sum_of_inputs_vs_sum_of_outputs(simple_transaction, utxos):
    assert simple_transaction.verify_sums()


def test_sum_of_outputs_is_higher_than_sum_of_outputs(simple_transaction, utxos):
    simple_transaction.outputs[0].value = 1000
    with pytest.raises(InputOutputSumsException):
        simple_transaction.verify_sums()

#
# def test_tries_to_spend_nonexistent_utxo(transfer_outputs, utxos):
#     tx = Transaction([TxInput(1, 2), transfer_outputs])
#     with pytest.raises(InputOutputSumsException):
#         tx.verify_sums()
