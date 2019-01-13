# pylint: disable=missing-docstring
from datetime import datetime, timedelta

from ecdsa import VerifyingKey, BadSignatureError
from multipledispatch import dispatch

from chasm.consensus import HASH_FUNC, CURVE
from chasm.consensus.primitives.transaction import Transaction, \
    SignedTransaction, OfferTransaction, MatchTransaction, \
    UnlockingDepositTransaction, ConfirmationTransaction, \
    MintingTransaction
from chasm.consensus.primitives.tx_output import TransferOutput, \
    XpeerFeeOutput, XpeerOutput
from chasm.consensus.tokens import ADDRESS_LENGTH, Tokens
from chasm.consensus.validation.validator import Validator
from chasm.maintenance.exceptions import DuplicatedInput, \
    NonexistentUTXO, InputOutputSumsException, \
    SignaturesAmountException, TransactionSizeException, \
    ReceiverUseXpeerOutputBeforeConfirmationError, \
    SenderUseXpeerOutputAfterConfirmationError, \
    SenderUseXpeerOutputBeforeTimeoutError, UnknownExchangeTokenError, \
    UseXpeerFeeOutputAsInputException, DepositValueError, \
    InvalidAddressLengthOutputError, DepositOutputError, \
    SendXpeerOutputWithoutExchangeError, MatchNonExistentOfferError, \
    SendXpeerFeeOutputError, NegativeOutput, OfferExistsError, \
    OutputIsNotXpeerFeeOutputError, InvalidAddressLengthPaymentError, \
    ExchangeAmountBelowZeroError, OfferTimeoutBeforeNow, \
    ConfFeeIndexOutOfRangeError, XpeerFeeOutputException, \
    XpeerOutputException
from chasm.serialization.rlp_serializer import RLPSerializer

MAX_SIZE = 2 ** 20


class TxValidator(Validator):
    def __init__(self, utxos, active_offers, accepted_offers):
        self._utxos = utxos
        self._active_offers = active_offers
        self._accepted_offers = accepted_offers
        self._rlp_serializer = RLPSerializer()

    @staticmethod
    @dispatch(SignedTransaction)
    def prepare(tx):
        return {'tx': tx.transaction, 'signatures': tx.signatures}

    @staticmethod
    @dispatch(MintingTransaction)
    def prepare(tx):
        return {'tx': tx, 'signatures': list()}

    def check_size(self, tx):
        data = self._rlp_serializer.encode(tx)
        if len(data) > MAX_SIZE:
            raise TransactionSizeException(tx.hash(), len(data))
        return True

    @staticmethod
    def check_outputs_are_positive(tx):
        for i, output in enumerate(tx.outputs):
            if output.value < 0:
                raise NegativeOutput(tx.hash(), i)

        return True

    @staticmethod
    def check_inputs_repetitions(tx):
        checked = []
        for tx_input in tx.inputs:
            if (tx_input.tx_hash, tx_input.output_no) in checked:
                raise DuplicatedInput(tx.hash(), tx_input.tx_hash.hex(),
                                      tx_input.output_no)
            checked.append((tx_input.tx_hash, tx_input.output_no))
        return True

    def check_sums(self, tx):
        utxos = self._get_input_utxos(tx)
        input_sum = sum(utxo.value for utxo in utxos)
        output_sum = sum(output.value for output in tx.outputs)
        if input_sum < output_sum:
            raise InputOutputSumsException(tx.hash(),
                                           input_sum,
                                           output_sum)
        return True

    def check_signatures(self, tx, signatures):
        if len(tx.inputs) != len(signatures):
            raise SignaturesAmountException(tx.hash(),
                                            len(tx.inputs),
                                            len(signatures))
        utxos = self._get_input_utxos(tx)
        for utxo, signature in zip(utxos, signatures):
            self._validate_signature(utxo, signature, tx)

        return True

    @dispatch(TransferOutput, bytes, Transaction)
    def _validate_signature(self, utxo, signature, tx):
        vk = VerifyingKey.from_string(utxo.receiver, curve=CURVE, hashfunc=HASH_FUNC)
        vk.verify(signature, tx.encoded)
        return True

    @dispatch(XpeerFeeOutput, bytes, Transaction)
    def _validate_signature(self, utxo, signature, tx):
        return True

    @dispatch(XpeerOutput, bytes, Transaction)
    def _validate_signature(self, utxo: XpeerOutput, signature, tx):
        try:
            # receiver
            vk_1 = VerifyingKey.from_string(utxo.receiver, curve=CURVE, hashfunc=HASH_FUNC)
            vk_1.verify(signature, tx.encoded)
            if utxo.exchange in self._accepted_offers:
                raise ReceiverUseXpeerOutputBeforeConfirmationError(tx.hash(), utxo.exchange)
        except BadSignatureError:
            # sender
            vk_1 = VerifyingKey.from_string(utxo.sender, curve=CURVE, hashfunc=HASH_FUNC)
            vk_1.verify(signature, tx.encoded)
            if utxo.exchange not in self._accepted_offers:
                raise SenderUseXpeerOutputAfterConfirmationError(tx.hash(), utxo.exchange)

            timeout = datetime.fromtimestamp(self._accepted_offers.get(utxo.exchange)[2])
            timeout += timedelta(days=14)
            if datetime.now() < timeout:
                raise SenderUseXpeerOutputBeforeTimeoutError(tx.hash(), utxo.exchange)

        return True

    def _get_utxo(self, tx_hash, tx_input):
        key = (tx_input.tx_hash, tx_input.output_no)
        if key not in self._utxos:
            raise NonexistentUTXO(tx_hash, tx_input.tx_hash,
                                  tx_input.output_no)
        return self._utxos.get((tx_input.tx_hash, tx_input.output_no))

    def _get_input_utxos(self, tx):
        utxos = []
        for tx_input in tx.inputs:
            utxos.append(self._get_utxo(tx.hash(), tx_input))

        return utxos

    def check_inputs_are_utxos(self, tx):
        self._get_input_utxos(tx)
        return True

    def check_type_specifics(self, tx):
        self._do_specific_validation(tx)
        return True

    @dispatch(MintingTransaction)
    def _do_specific_validation(self, tx):
        return True

    @dispatch(Transaction)
    def _do_specific_validation(self, tx):
        return TxValidator.BaseTxValidator(self._utxos,
                                           self._accepted_offers). \
            validate(tx)

    @dispatch(OfferTransaction)
    def _do_specific_validation(self, tx: OfferTransaction):
        return TxValidator.OfferValidator(self._utxos,
                                          self._accepted_offers). \
            validate(tx)

    @dispatch(MatchTransaction)
    def _do_specific_validation(self, tx: MatchTransaction):
        return TxValidator.AcceptanceValidator(self._utxos,
                                               self._accepted_offers,
                                               self._active_offers). \
            validate(tx)

    @dispatch(ConfirmationTransaction)
    def _do_specific_validation(self, tx: ConfirmationTransaction):
        return TxValidator.ConfirmationValidator(self._utxos,
                                                 self._accepted_offers). \
            validate(tx)

    @dispatch(UnlockingDepositTransaction)
    def _do_specific_validation(self, tx: UnlockingDepositTransaction):
        return TxValidator.DepositUnlockValidator(self._utxos,
                                                  self._accepted_offers,
                                                  self._active_offers). \
            validate(tx)

    class TransactionValidator(Validator):
        def __init__(self, utxos, accepted_offers):
            self._utxos = utxos
            self._accepted_offers = accepted_offers

        @staticmethod
        def _validate_address_length(token, address):
            return len(address) == ADDRESS_LENGTH.get(token)

        @staticmethod
        def prepare(self, obj):
            return {'tx': obj}

        @dispatch(object)
        def _validate_output(self, arg, *args):
            raise NotImplementedError

        @dispatch(TransferOutput)
        def _validate_output(self, output):
            return self._validate_address_length(Tokens.XPEER.value,
                                                 output.receiver)

        @dispatch(XpeerOutput)
        def _validate_output(self, output: XpeerOutput):
            if output.exchange not in self._accepted_offers:
                raise XpeerOutputException

            return self._validate_address_length(Tokens.XPEER.value,
                                                 output.receiver) and \
                   self._validate_address_length(Tokens.XPEER.value,
                                                 output.sender)

        @dispatch(XpeerFeeOutput, int, bytes)
        def _validate_output(self, output):
            raise XpeerFeeOutputException

        def _validate_outputs(self, tx):
            for i, output in enumerate(tx.outputs):
                try:
                    if self._validate_output(output) is False:
                        raise InvalidAddressLengthOutputError(tx.hash(), i)
                except XpeerOutputException:
                    raise SendXpeerOutputWithoutExchangeError(tx.hash, i)
                except XpeerFeeOutputException:
                    SendXpeerFeeOutputError(tx.hash(), i)
            return True

        def _validate_inputs(self, tx):
            for tx_input in tx.inputs:
                if isinstance(self._utxos.get((tx_input.tx_hash,
                                               tx_input.output_no)),
                              XpeerFeeOutput):
                    raise UseXpeerFeeOutputAsInputException(tx.hash())
            return True

    class ExchangeSideTransactionValidator(TransactionValidator):
        def __init__(self, utxos, accepted_offers):
            self._utxos = utxos
            self._accepted_offers = accepted_offers

        @dispatch(XpeerFeeOutput)
        def _validate_output(self, output):
            return True

        def _validate_deposit(self, tx):
            if len(tx.outputs) <= tx.deposit_index:
                raise DepositOutputError
            output_sum = sum(output.value for output in tx.outputs)
            input_sum = 0
            for tx_input in tx.inputs:
                utxo = self._utxos.get(tx_input.tx_hash, tx_input.output_no)
                input_sum += utxo.value
            tx_fee = input_sum - output_sum
            if tx.outputs[tx.deposit_index].value < tx_fee * 10:
                raise DepositValueError(tx.hash(), tx.deposit_index,
                                        tx.outputs[tx.deposit_index].value,
                                        tx_fee * 10)

            return True

        @staticmethod
        def _validate_confirmation_fee(tx):
            if len(tx.outputs) < tx.confirmation_fee_index:
                raise ConfFeeIndexOutOfRangeError(tx.hash(),
                                                  tx.confirmation_fee_index)
            if isinstance(tx.outputs[tx.confirmation_fee_index],
                          XpeerFeeOutput) is False:
                raise OutputIsNotXpeerFeeOutputError(tx.hash(),
                                                     tx.confirmation_fee_index)
            return True

    class BaseTxValidator(TransactionValidator):
        def __init__(self, utxos, accepted_offers):
            super().__init__(utxos, accepted_offers)

        def prepare(self, obj):
            return {'tx': obj}

        def check_outputs(self, tx):
            return self._validate_outputs(tx)

        def check_inputs(self, tx):
            return self._validate_inputs(tx)

    class OfferValidator(ExchangeSideTransactionValidator):
        def __init__(self, utxos, accepted_offers, active_offers):
            self._active_offers = active_offers
            super().__init__(utxos, accepted_offers)

        def check_outputs(self, tx):
            return self._validate_outputs(tx)

        def check_inputs(self, tx):
            return self._validate_inputs(tx)

        def check_if_exist(self, tx):
            if tx.hash() in self._active_offers:
                raise OfferExistsError(tx.hash)

        @staticmethod
        def _validate_token(token):
            return token in ADDRESS_LENGTH.keys()

        def check_token(self, tx):
            if self._validate_token(tx.token_in) is False:
                raise UnknownExchangeTokenError(tx.hash(), tx.token_in)
            return True

        def check_expected(self, tx):
            if self._validate_token(tx.token_out) is False:
                raise UnknownExchangeTokenError(tx.hash(), tx.token_out)
            return True

        @staticmethod
        def check_amount(tx):
            if tx.value_in < 0:
                raise ExchangeAmountBelowZeroError(tx.hash(), tx.token_in,
                                                   tx.value_in)
            return True

        @staticmethod
        def check_price(tx):
            if tx.value_out < 0:
                raise ExchangeAmountBelowZeroError(tx.hash(), tx.token_out,
                                                   tx.value_out)
            return True

        @staticmethod
        def check_timeout(tx):
            timeout = datetime.fromtimestamp(tx.timeout)
            if timeout < datetime.now():
                raise OfferTimeoutBeforeNow(tx.hash(), timeout)

            return True

        def check_deposit(self, tx):
            return self._validate_deposit(tx)

        def check_confirmation_fee(self, tx):
            return self._validate_confirmation_fee(tx)

        def check_payment_address(self, tx):
            if self._validate_address_length(tx.token_out, tx.address_out):
                raise InvalidAddressLengthPaymentError(tx.hash(),
                                                       len(tx.address_out),
                                                       tx.token_out)
            return True

    class AcceptanceValidator(ExchangeSideTransactionValidator):
        def __init__(self, utxos, accepted_offers, active_offers):
            self._active_offers = active_offers
            super().__init__(utxos, accepted_offers)

        def check_outputs(self, tx):
            return self._validate_outputs(tx)

        def check_inputs(self, tx):
            return self._validate_inputs(tx)

        def check_deposit(self, tx):
            return self._validate_deposit(tx)

        def check_confirmation_fee(self, tx):
            return self._validate_confirmation_fee(tx)

        def check_payment_address(self, tx):
            offer = self._active_offers.get(tx.exchange)
            token = offer.token_in
            if self._validate_address_length(token, tx.address_in):
                raise InvalidAddressLengthPaymentError(tx.hash(),
                                                       len(tx.address_in),
                                                       token)

        def check_if_offer_exists(self, tx: MatchTransaction):
            if tx.exchange not in self._active_offers:
                raise MatchNonExistentOfferError(tx.hash(), tx.exchange)
            return True

    class ConfirmationValidator(TransactionValidator):
        def __init__(self, utxos, accepted_offers):
            super().__init__(utxos, accepted_offers)

        def check_inputs(self, tx):
            raise NotImplementedError

        def check_outputs(self, tx):
            raise NotImplementedError

        def check_exchange(self, tx):
            raise NotImplementedError

        def check_proof_in(self, tx):
            # Currently we have no mechanism to validate other tokens
            raise NotImplementedError

        def check_proof_out(self, tx):
            raise NotImplementedError

    class DepositUnlockValidator(TransactionValidator):
        def __init__(self, utxos, accepted_offers, active_offers):
            self._active_offers = active_offers
            super().__init__(utxos, accepted_offers)

        def check_inputs(self, tx):
            raise NotImplementedError

        def check_outputs(self, tx):
            raise NotImplementedError

        def check_exchange(self, tx):
            raise NotImplementedError

        def check_side(self, tx):
            raise NotImplementedError

        def check_proof(self, tx):
            # Currently we have no mechanism to validate other tokens
            raise NotImplementedError
