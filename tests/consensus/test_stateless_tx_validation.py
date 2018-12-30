import pytest
from ecdsa import VerifyingKey
from pytest import fixture

from chasm import consensus
from chasm.primitives.transaction import Transaction
from chasm.primitives.tx_input import TxInput
from chasm.primitives.tx_output import TxTransferOutput
from chasm.serialization.serializer import Serializer


@fixture
def inputs():
    return [TxInput(1, 1), TxInput(10, 100), TxInput(2, 1)]


@fixture
def utxos(inputs, alice, bob, carol):
    utxos = dict()
    for (input, entity) in zip(inputs, [alice, bob, carol]):
        utxos[input] = TxTransferOutput(100, entity.pub)
    return utxos


@fixture
def transfer_outputs(alice, bob):
    return [TxTransferOutput(100, alice.pub), TxTransferOutput(10, bob.pub)]


@fixture
def simple_transaction(inputs, transfer_outputs):
    return Transaction(inputs, transfer_outputs)


@fixture
def signed_simple_transaction(simple_transaction, alice, bob, carol):
    return None


def test_sign_transaction_and_manually_verify_signature(simple_transaction, alice, bob):
    entities = [alice, bob]
    for entity in entities:
        signature = simple_transaction.sign(entity.priv)
        vk = VerifyingKey.from_string(entity.pub, curve=consensus.CURVE)
        encoded = Serializer.encode(simple_transaction)
        assert vk.verify(signature, encoded, consensus.HASH_FUNC)


def test_sign_and_verify_signature(simple_transaction, alice, bob):
    entities = [alice, bob]
    for entity in entities:
        assert simple_transaction.verify_signature(entity.pub, simple_transaction.sign(entity.priv))


def test_verifies_invalid_signature(simple_transaction, alice, bob):
    assert not simple_transaction.verify_signature(alice.pub, simple_transaction.sign(bob.priv))


def test_verifies_sum_of_inputs_vs_sum_of_outputs(simple_transaction, utxos):
    assert simple_transaction.verify_sums(utxos)


def test_sum_of_outputs_is_higher_than_sum_of_outputs(simple_transaction, utxos):
    simple_transaction.outputs[0].value = 1000
    assert not simple_transaction.verify_sums(utxos)


def test_tries_to_spend_nonexistent_utxo(transfer_outputs, utxos):
    tx = Transaction([TxInput(1, 2), transfer_outputs])
    with pytest.raises(Exception):
        tx.verify_sums(utxos)
