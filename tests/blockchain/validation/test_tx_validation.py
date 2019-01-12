# pylint: disable=missing-docstring,redefined-outer-name,invalid-name
from pytest import fixture, raises

from chasm.consensus.primitives.transaction import Transaction, SignedTransaction
from chasm.consensus.primitives.tx_input import TxInput
from chasm.consensus.primitives.tx_output import TransferOutput
from chasm.consensus.validation.tx_validator import TxValidator
from chasm.maintenance.exceptions import DuplicatedInput, NonexistentUTXO


@fixture
def inputs():
    return [TxInput(b'1', 1), TxInput(b'10', 100), TxInput(b'2', 1)]


@fixture
def utxos(inputs, alice, bob, carol):
    utxos = {}
    for tx_input, entity in zip(inputs, [alice, bob, carol]):
        utxos[(tx_input.tx_hash, tx_input.output_no)] = TransferOutput(100, entity.pub)

    return utxos


@fixture
def transfer_outputs(alice, bob):
    return [TransferOutput(100, alice.pub), TransferOutput(10, bob.pub)]


@fixture
def simple_transaction(inputs, transfer_outputs):
    tx = Transaction(inputs, transfer_outputs)
    return tx


@fixture
def signed_simple_transaction(simple_transaction, alice, bob, carol):
    return SignedTransaction.build_signed(simple_transaction,
                                          [alice.priv,
                                           bob.priv,
                                           carol.priv])


@fixture
def validator():
    def _get_validator(utxos_=dict(), dutxos_=dict(),
                       active_offers_=None, accepted_offers_=None):
        return TxValidator(utxos=utxos_, dutxos=dutxos_,
                           active_offers=active_offers_, accepted_offers=accepted_offers_)

    return _get_validator


def test_tries_to_spend_duplicated_input(validator, simple_transaction):
    simple_transaction.inputs[1] = simple_transaction.inputs[0]
    with raises(DuplicatedInput):
        validator().check_inputs_repetitions(simple_transaction)


def test_spend_duplicated_input(validator, simple_transaction):
    assert validator().check_inputs_repetitions(simple_transaction)


def test_tries_to_spend_nonexistent_utxo(validator, simple_transaction):
    with raises(NonexistentUTXO):
        validator().check_inputs_are_utxos(simple_transaction)


def test_nonexistent_utxo(validator, utxos, simple_transaction):
    assert validator(utxos).check_inputs_are_utxos(simple_transaction)
