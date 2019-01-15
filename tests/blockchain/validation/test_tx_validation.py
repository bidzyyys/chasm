# pylint: disable=missing-docstring,redefined-outer-name,invalid-name
import datetime
import time

from ecdsa import BadSignatureError
from pytest import fixture, raises

from chasm.consensus.primitives.transaction import Transaction, SignedTransaction, OfferTransaction
from chasm.consensus.primitives.tx_input import TxInput
from chasm.consensus.primitives.tx_output import TransferOutput, XpeerOutput, XpeerFeeOutput
from chasm.consensus.tokens import Tokens
from chasm.consensus.validation.tx_validator import TxValidator
from chasm.maintenance.exceptions import DuplicatedInput, NonexistentUTXO, \
    InputOutputSumsException, SignaturesAmountException, TransactionSizeException, \
    UseXpeerFeeOutputAsInputException, NegativeOutput, OfferTimeoutBeforeNowError, \
    UnknownExchangeTokenError, OfferExistsError, DepositOutputError, DepositValueError, \
    OutputIsNotXpeerFeeOutputError, ConfFeeIndexOutOfRangeError, InvalidAddressLengthOutputError, \
    InvalidAddressLengthPaymentError, SendXpeerFeeOutputError, SendXpeerOutputWithoutExchangeError, \
    ReceiverUseXpeerOutputBeforeConfirmationError, SenderUseXpeerOutputAfterConfirmationError, \
    SenderUseXpeerOutputBeforeTimeoutError


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
def xpeer_fee_output():
    return XpeerFeeOutput(2)


@fixture
def xpeer_output(alice, bob):
    return XpeerOutput(2, sender=alice.pub, receiver=bob.pub, exchange=b'a')


@fixture
def deposit(alice):
    return TransferOutput(12, receiver=alice.pub)


@fixture
def own_transfer(alice):
    return TransferOutput(85, receiver=alice.pub)


@fixture
def exchange_side_outputs(xpeer_fee_output, deposit, own_transfer):
    return [deposit, xpeer_fee_output, own_transfer]


@fixture
def exchange_side_inputs():
    return [TxInput(b'1', 1)]


@fixture(scope='session')
def btc_addr():
    return b'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'


@fixture(scope='session')
def eth_addr():
    return b'aaaaaaaaaaaaaaaaaaaa'


@fixture(scope='session')
def proof():
    return b'aaaa1234'


@fixture(scope='session')
def timeout():
    dt = datetime.datetime.now()
    dt += datetime.timedelta(days=1)
    return to_timestamp(dt)


def to_timestamp(date):
    return int(time.mktime(date.timetuple()))


@fixture
def simple_offer(exchange_side_inputs, exchange_side_outputs, btc_addr, timeout):
    return OfferTransaction(inputs=exchange_side_inputs,
                            outputs=exchange_side_outputs,
                            token_in=Tokens.XPEER.value,
                            token_out=Tokens.BITCOIN.value, value_in=100,
                            value_out=1, address_out=btc_addr,
                            deposit_index=0, confirmation_fee_index=1,
                            timeout=timeout)


@fixture
def utxos_xpeer_output(exchange_side_inputs, alice, bob, xpeer_output):
    return {
        (exchange_side_inputs[0].tx_hash, exchange_side_inputs[0].output_no): xpeer_output
    }


@fixture
def too_much_signed_simple_transaction(signed_simple_transaction):
    for _ in range(13):
        signed_simple_transaction.transaction.outputs.extend(
            signed_simple_transaction.transaction.outputs.copy())

    return signed_simple_transaction


@fixture
def validator():
    def _get_validator(utxos_=dict(),
                       active_offers_=dict(), accepted_offers_=dict()):
        return TxValidator(utxos=utxos_,
                           active_offers=active_offers_, accepted_offers=accepted_offers_)

    return _get_validator


def test_tries_to_spend_duplicated_input(validator, simple_transaction):
    simple_transaction.inputs[1] = simple_transaction.inputs[0]
    with raises(DuplicatedInput):
        validator().check_inputs_repetitions(simple_transaction)


def test_spend_duplicated_input(validator, simple_transaction):
    assert validator().check_inputs_repetitions(simple_transaction)


def test_tries_to_send_negative_output(validator, utxos, simple_transaction):
    simple_transaction.outputs[0].value = -10
    with raises(NegativeOutput):
        validator(utxos).check_outputs_are_positive(simple_transaction)


def test_send_negative_output(validator, utxos, simple_transaction):
    validator(utxos).check_outputs_are_positive(simple_transaction)


def test_tries_to_spend_nonexistent_utxo(validator, simple_transaction):
    with raises(NonexistentUTXO):
        validator().check_inputs_are_utxos(simple_transaction)


def test_nonexistent_utxo(validator, utxos, simple_transaction):
    assert validator(utxos).check_inputs_are_utxos(simple_transaction)


def test_verifies_sum_of_inputs_vs_sum_of_outputs(validator, utxos, simple_transaction):
    assert validator(utxos).check_sums(simple_transaction)


def test_sum_of_outputs_is_higher_than_sum_of_outputs(validator, utxos, simple_transaction):
    simple_transaction.outputs[0].value = 1000
    with raises(InputOutputSumsException):
        validator(utxos).check_sums(simple_transaction)


def test_verifies_different_signature_count(validator, utxos, simple_transaction):
    with raises(SignaturesAmountException):
        validator(utxos).check_signatures(simple_transaction, [])


def test_verifies_invalid_signature(validator, utxos, signed_simple_transaction):
    with raises(BadSignatureError):
        validator(utxos).check_signatures(signed_simple_transaction.transaction,
                                          signed_simple_transaction.signatures[::-1])


def test_verifies_signature(validator, utxos, signed_simple_transaction):
    assert validator(utxos).check_signatures(signed_simple_transaction.transaction,
                                             signed_simple_transaction.signatures)


def test_tx_size(validator, signed_simple_transaction):
    assert validator().check_size(signed_simple_transaction)


def test_tx_has_too_much_size(validator, too_much_signed_simple_transaction):
    with raises(TransactionSizeException):
        validator().check_size(too_much_signed_simple_transaction)


def test_verify_valid_transaction(validator, utxos, signed_simple_transaction):
    validator(utxos).validate(signed_simple_transaction)


def test_invalid_utxos_transaction(validator, signed_simple_transaction):
    with raises(NonexistentUTXO):
        validator().validate(signed_simple_transaction)


def test_invalid_inputs_transaction(validator, utxos, signed_simple_transaction):
    signed_simple_transaction.transaction.inputs[1] = \
        signed_simple_transaction.transaction.inputs[0]
    with raises(DuplicatedInput):
        validator(utxos).validate(signed_simple_transaction)


def test_invalid_signatures_len_transaction(validator, utxos, signed_simple_transaction):
    del signed_simple_transaction.signatures[1:]
    with raises(SignaturesAmountException):
        validator(utxos).validate(signed_simple_transaction)


def test_invalid_signatures_transaction(validator, utxos, signed_simple_transaction):
    signed_simple_transaction.signatures[1] = \
        signed_simple_transaction.signatures[0]
    with raises(BadSignatureError):
        validator(utxos).validate(signed_simple_transaction)


def test_invalid_size_transaction(validator, utxos, too_much_signed_simple_transaction):
    with raises(TransactionSizeException):
        validator(utxos).validate(too_much_signed_simple_transaction)


def test_verify_invalid_sums(validator, utxos, signed_simple_transaction):
    signed_simple_transaction.outputs[0].value = 1000
    with raises(InputOutputSumsException):
        validator(utxos).validate(signed_simple_transaction)


def test_verify_simple_transfer_use_xpeer_fee_output(validator, utxos, xpeer_fee_output, signed_simple_transaction):
    utxos[(b'1', 1)] = xpeer_fee_output
    with raises(UseXpeerFeeOutputAsInputException):
        validator(utxos).validate(signed_simple_transaction)


def test_verify_valid_offer(validator, utxos, simple_offer, alice):
    signed_tx = SignedTransaction.build_signed(simple_offer, [alice.priv])
    assert validator(utxos).validate(signed_tx)


def test_verify_offer_invalid_timeout(validator, utxos, simple_offer: OfferTransaction, alice):
    simple_offer.timeout = to_timestamp(datetime.datetime.now())
    signed_tx = SignedTransaction.build_signed(simple_offer, [alice.priv])
    with raises(OfferTimeoutBeforeNowError):
        validator(utxos).validate(signed_tx)


def test_verify_offer_invalid_token_in(validator, utxos, simple_offer: OfferTransaction, alice):
    simple_offer.token_in = 4
    signed_tx = SignedTransaction.build_signed(simple_offer, [alice.priv])
    with raises(UnknownExchangeTokenError):
        validator(utxos).validate(signed_tx)


def test_verify_offer_that_exists(validator, utxos, simple_offer: OfferTransaction, alice):
    signed_tx = SignedTransaction.build_signed(simple_offer, [alice.priv])
    with raises(OfferExistsError):
        validator(utxos, {simple_offer.hash(): simple_offer}).validate(signed_tx)


def test_verify_offer_deposit_not_transfer_output(validator, utxos, simple_offer: OfferTransaction, alice):
    simple_offer.deposit_index = 1
    signed_tx = SignedTransaction.build_signed(simple_offer, [alice.priv])
    with raises(DepositOutputError):
        validator(utxos).validate(signed_tx)


def test_verify_offer_deposit_out_of_range(validator, utxos, simple_offer: OfferTransaction, alice):
    simple_offer.deposit_index = 6
    signed_tx = SignedTransaction.build_signed(simple_offer, [alice.priv])
    with raises(DepositOutputError):
        validator(utxos).validate(signed_tx)


def test_verify_offer_deposit_too_small_value(validator, utxos, simple_offer: OfferTransaction, alice):
    simple_offer.outputs[simple_offer.deposit_index].value = 1
    signed_tx = SignedTransaction.build_signed(simple_offer, [alice.priv])
    with raises(DepositValueError):
        validator(utxos).validate(signed_tx)


def test_verify_offer_confirmation_not_xpeer_fee_output(validator, utxos, simple_offer: OfferTransaction, alice):
    simple_offer.confirmation_fee_index = 0
    signed_tx = SignedTransaction.build_signed(simple_offer, [alice.priv])
    with raises(OutputIsNotXpeerFeeOutputError):
        validator(utxos).validate(signed_tx)


def test_verify_offer_confirmation_out_of_range(validator, utxos, simple_offer: OfferTransaction, alice):
    simple_offer.confirmation_fee_index = 6
    signed_tx = SignedTransaction.build_signed(simple_offer, [alice.priv])
    with raises(ConfFeeIndexOutOfRangeError):
        validator(utxos).validate(signed_tx)


def test_verify_offer_invalid_payment_address(validator, utxos, simple_offer: OfferTransaction, alice):
    simple_offer.address_out = b'a'
    signed_tx = SignedTransaction.build_signed(simple_offer, [alice.priv])
    with raises(InvalidAddressLengthPaymentError):
        validator(utxos).validate(signed_tx)


def test_verify_offer_invalid_own_payment_address_len(validator, utxos, simple_offer: OfferTransaction, alice):
    simple_offer.outputs[-1].receiver = b'a'
    signed_tx = SignedTransaction.build_signed(simple_offer, [alice.priv])
    with raises(InvalidAddressLengthOutputError):
        validator(utxos).validate(signed_tx)


def test_transfer_send_xpeer_fee_output(validator, utxos, simple_transaction, xpeer_fee_output, alice, bob, carol):
    simple_transaction.outputs = [xpeer_fee_output]
    signed_tx = SignedTransaction.build_signed(simple_transaction, [alice.priv, bob.priv, carol.priv])
    with raises(SendXpeerFeeOutputError):
        validator(utxos).validate(signed_tx)


def test_transfer_send_xpeer_output_without_exchange(validator, utxos, simple_transaction, xpeer_output, alice, bob,
                                                     carol):
    simple_transaction.outputs = [xpeer_output]
    signed_tx = SignedTransaction.build_signed(simple_transaction, [alice.priv, bob.priv, carol.priv])
    with raises(SendXpeerOutputWithoutExchangeError):
        validator(utxos).validate(signed_tx)


def test_transfer_send_xpeer_output_valid_exchange(validator, utxos, simple_transaction, xpeer_output, alice, bob,
                                                   carol, simple_offer):
    xpeer_output.exchange = simple_offer.hash()
    simple_transaction.outputs = [xpeer_output]
    signed_tx = SignedTransaction.build_signed(simple_transaction, [alice.priv, bob.priv, carol.priv])
    assert validator(utxos, {}, {simple_offer.hash(): list()}).validate(signed_tx)


def test_transfer_receiver_use_xpeer_output_before_confirmation(validator, utxos_xpeer_output, xpeer_output,
                                                                exchange_side_inputs, bob,
                                                                simple_offer):
    xpeer_output.exchange = simple_offer.hash()
    tx = Transaction(inputs=exchange_side_inputs, outputs=[xpeer_output])
    signed_tx = SignedTransaction.build_signed(tx, [bob.priv])
    with raises(ReceiverUseXpeerOutputBeforeConfirmationError):
        validator(utxos_xpeer_output, {}, {simple_offer.hash(): list()}).validate(signed_tx)


def test_transfer_receiver_use_xpeer_output_after_confirmation(validator, utxos_xpeer_output,
                                                               exchange_side_inputs, bob,
                                                               simple_offer):
    xpeer_output.exchange = simple_offer.hash()
    tx = Transaction(inputs=exchange_side_inputs, outputs=[TransferOutput(1, bob.pub)])
    signed_tx = SignedTransaction.build_signed(tx, [bob.priv])
    assert validator(utxos_xpeer_output, {}, {}).validate(signed_tx)


def test_transfer_sender_use_xpeer_output_after_confirmation(validator, utxos_xpeer_output, xpeer_output,
                                                             exchange_side_inputs, alice,
                                                             simple_offer):
    xpeer_output.exchange = simple_offer.hash()
    tx = Transaction(inputs=exchange_side_inputs, outputs=[TransferOutput(1, alice.pub)])
    signed_tx = SignedTransaction.build_signed(tx, [alice.priv])
    with raises(SenderUseXpeerOutputAfterConfirmationError):
        validator(utxos_xpeer_output, {}, {}).validate(signed_tx)


def test_transfer_sender_use_xpeer_output_before_timeout(validator, utxos_xpeer_output, xpeer_output,
                                                         exchange_side_inputs, alice,
                                                         simple_offer):
    xpeer_output.exchange = simple_offer.hash()
    tx = Transaction(inputs=exchange_side_inputs, outputs=[TransferOutput(1, alice.pub)])
    signed_tx = SignedTransaction.build_signed(tx, [alice.priv])
    with raises(SenderUseXpeerOutputBeforeTimeoutError):
        validator(utxos_xpeer_output, {}, {simple_offer.hash(): [
            None, None, to_timestamp(datetime.datetime.now())]
        }). \
            validate(signed_tx)


def test_transfer_sender_use_xpeer_output_after_timeout(validator, utxos_xpeer_output, xpeer_output,
                                                        exchange_side_inputs, alice,
                                                        simple_offer):
    xpeer_output.exchange = simple_offer.hash()
    tx = Transaction(inputs=exchange_side_inputs, outputs=[TransferOutput(1, alice.pub)])
    signed_tx = SignedTransaction.build_signed(tx, [alice.priv])
    assert validator(utxos_xpeer_output, {}, {simple_offer.hash(): [
        None, None, to_timestamp(datetime.datetime.now() - datetime.timedelta(days=15))
    ]}). \
        validate(signed_tx)
