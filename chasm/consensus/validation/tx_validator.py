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
    SenderUseXpeerOutputBeforeTimeoutError, \
    UseXpeerFeeOutputExceptionAsInput, \
    InvalidAddressLengthOutputError, \
    SendXpeerOutputWithoutExchangeError, \
    SendXpeerFeeOutputError
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

    def check_inputs_repetitions(self, tx):
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

    @dispatch(MintingTransaction)
    def check_type_specifics(self, tx):
        return True

    @dispatch(Transaction)
    def do_specific_validation(self, tx, ):
        return TxValidator.BaseTxValidator(self._utxos,
                                           self._accepted_offers). \
            validate(tx)

    @dispatch(OfferTransaction, list)
    def do_specific_validation(self, tx: OfferTransaction):
        return TxValidator.OfferValidator(self._utxos,
                                          self._accepted_offers). \
            validate(tx)

    @dispatch(MatchTransaction, list)
    def do_specific_validation(self, tx: MatchTransaction):
        return TxValidator.AcceptanceValidator(self._utxos,
                                               self._accepted_offers,
                                               self._active_offers). \
            validate(tx)

    @dispatch(ConfirmationTransaction, list)
    def do_specific_validation(self, tx: ConfirmationTransaction):
        return TxValidator.ConfirmationValidator(self._utxos,
                                                 self._accepted_offers). \
            validate(tx)

    @dispatch(UnlockingDepositTransaction, list)
    def do_specific_validation(self, tx: UnlockingDepositTransaction):
        return TxValidator.DepositUnlockValidator(self._utxos,
                                                  self._accepted_offers,
                                                  self._active_offers). \
            validate(tx)

    class TransactionValidator(Validator):
        def __init__(self, utxos, accepted_offers):
            self._utxos = utxos
            self._accepted_offers = accepted_offers

        @staticmethod
        def prepare(self, obj):
            return {'tx': obj}

        @dispatch(TransferOutput, int, bytes)
        def _validate_output(self, output: TransferOutput, output_no, tx_hash):
            if len(output.receiver) < ADDRESS_LENGTH.get(Tokens.XPEER.value):
                raise InvalidAddressLengthOutputError(tx_hash, len(output.receiver),
                                                      output_no)
            return True

        @dispatch(XpeerOutput, int, bytes)
        def _validate_output(self, output: XpeerOutput, output_no, tx_hash):
            if len(output.receiver) < ADDRESS_LENGTH.get(Tokens.XPEER.value):
                raise InvalidAddressLengthOutputError(tx_hash, len(output.receiver),
                                                      output_no)
            if output.exchange not in self._accepted_offers:
                raise SendXpeerOutputWithoutExchangeError(tx_hash, output_no)

        @dispatch(XpeerFeeOutput, int, bytes)
        def _validate_output(self, output, output_no, tx_hash):
            raise SendXpeerFeeOutputError(tx_hash, output_no)

    class BaseTxValidator(TransactionValidator):
        def __init__(self, utxos, accepted_offers):
            super().__init__(utxos, accepted_offers)

        def prepare(self, obj):
            return {'tx': obj}

        def check_outputs(self, tx):
            self._validate_output(tx)

        def check_inputs(self, tx):
            for tx_input in tx.inputs:
                if isinstance(self._utxos.get((tx_input.tx_hash,
                                               tx_input.output_no)),
                              XpeerFeeOutput):
                    raise UseXpeerFeeOutputExceptionAsInput(tx.hash())

    class OfferValidator(TransactionValidator):
        def __init__(self, utxos, accepted_offers, active_offers):
            self._active_offers = active_offers
            super().__init__(utxos, accepted_offers)

        def check_does_not_use_fees_as_inputs(self):
            # TODO
            pass

    class AcceptanceValidator(TransactionValidator):
        def __init__(self, utxos, accepted_offers, active_offers):
            self._active_offers = active_offers
            super().__init__(utxos, accepted_offers)

        def check_does_not_use_fees_as_inputs(self):
            # TODO
            pass

    class ConfirmationValidator(TransactionValidator):
        def __init__(self, utxos, accepted_offers):
            super().__init__(utxos, accepted_offers)

        def check_uses_fees_inputs_from_the_right_exchange(self):
            # TODO
            pass

    class DepositUnlockValidator(TransactionValidator):
        def __init__(self, utxos, accepted_offers, active_offers):
            self._active_offers = active_offers
            super().__init__(utxos, accepted_offers)
