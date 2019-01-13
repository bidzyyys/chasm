# pylint: disable=missing-docstring
from ecdsa import VerifyingKey
from multipledispatch import dispatch

from chasm.consensus import HASH_FUNC, CURVE
from chasm.consensus.primitives.transaction import Transaction, \
    SignedTransaction, OfferTransaction, MatchTransaction, \
    UnlockingDepositTransaction, ConfirmationTransaction, \
    MintingTransaction
from chasm.consensus.validation.validator import Validator
from chasm.maintenance.exceptions import DuplicatedInput, \
    NonexistentUTXO, InputOutputSumsException, \
    SignaturesAmountException, TransactionSizeException
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
            vk = VerifyingKey.from_string(utxo.receiver, curve=CURVE, hashfunc=HASH_FUNC)
            vk.verify(signature, tx.encoded)

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
        self.do_specific_validation(tx)

    @dispatch(object)
    def do_specific_validation(self, arg, *args):
        raise NotImplementedError

    @dispatch(Transaction)
    def do_specific_validation(self, tx: Transaction):
        return TxValidator.BaseTxValidator(). \
            validate(tx)

    @dispatch(OfferTransaction)
    def do_specific_validation(self, tx: OfferTransaction):
        return TxValidator.OfferValidator(). \
            validate(tx)

    @dispatch(MatchTransaction)
    def do_specific_validation(self, tx: MatchTransaction):
        return TxValidator.MatchTransactionValidator(). \
            validate(tx)

    @dispatch(ConfirmationTransaction)
    def do_specific_validation(self, tx: ConfirmationTransaction):
        return TxValidator.ConfirmationValidator(). \
            validate(tx)

    @dispatch(UnlockingDepositTransaction)
    def do_specific_validation(self, tx: UnlockingDepositTransaction):
        return TxValidator.DepositUnlockValidator(). \
            validate(tx)

    @dispatch(MintingTransaction)
    def do_specific_validation(self, tx: MintingTransaction):
        return TxValidator.MintingTransactionValidator(). \
            validate(tx)

    class OfferValidator(Validator):
        def check_does_not_use_fees_as_inputs(self):
            # TODO
            pass

    class AcceptanceValidator(Validator):
        def check_does_not_use_fees_as_inputs(self):
            # TODO
            pass

    class ConfirmationValidator(Validator):
        def check_uses_fees_inputs_from_the_right_exchange(self):
            # TODO
            pass

    class DepositUnlockValidator(Validator):
        # TODO
        pass

    class MatchTransactionValidator(Validator):
        # TODO
        pass

    class MintingTransactionValidator(Validator):
        # TODO
        pass

    class BaseTxValidator(Validator):

        @staticmethod
        def prepare(obj):
            return {'tx': obj}

        def check_does_not_use_fees_as_inputs(self, tx):
            # TODO
            return True
