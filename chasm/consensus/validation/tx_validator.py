# pylint: disable=missing-docstring
from multipledispatch import dispatch

from chasm.consensus.primitives.transaction import Transaction, \
    SignedTransaction, OfferTransaction, MatchTransaction, \
    UnlockingDepositTransaction, ConfirmationTransaction, \
    MintingTransaction
from chasm.consensus.validation.validator import Validator
from chasm.maintenance.exceptions import DuplicatedInput


class TxValidator(Validator):
    def __init__(self, utxos, dutxos, active_offers, accepted_offers):
        self._utxos = utxos
        self._dutxos = dutxos
        self._active_offers = active_offers
        self._accepted_offers = accepted_offers

    @staticmethod
    @dispatch(SignedTransaction)
    def prepare(tx):
        return {'tx': tx.transaction, 'signatures': tx.signatures}

    @staticmethod
    @dispatch(MintingTransaction)
    def prepare(tx):
        return {'tx': tx, 'signatures': None}

    def check_size(self, tx):
        pass

    def check_inputs_repetitions(self, tx):
        checked = []
        for tx_input in tx.inputs:
            if (tx_input.tx_hash, tx_input.output_no) in checked:
                raise DuplicatedInput(tx.hash(),
                                      "tx_hash: {}, output_no: {}".
                                      format(tx_input.tx_hash.hex(),
                                             tx_input.output_no))
            checked.append((tx_input.tx_hash, tx_input.output_no))
        return True

    def check_outputs(self, tx):
        pass

    def check_sums(self, tx):
        pass

    def check_signatures(self, tx):
        pass

    def check_inputs_are_utxos(self, tx):
        pass

    def check_type_specifics(self, tx):
        self.do_specific_validation(tx)

    @dispatch(object)
    def do_specific_validation(self, arg, *args):
        raise NotImplementedError

    @dispatch(Transaction)
    def do_specific_validation(self, tx: Transaction):
        print("Transaction")
        return TxValidator.BaseTxValidator(). \
            validate(tx)

    @dispatch(OfferTransaction)
    def do_specific_validation(self, tx: OfferTransaction):
        print("Offer")
        return TxValidator.OfferValidator(). \
            validate(tx)

    @dispatch(MatchTransaction)
    def do_specific_validation(self, tx: MatchTransaction):
        print("Match")
        return TxValidator.MatchTransactionValidator(). \
            validate(tx)

    @dispatch(ConfirmationTransaction)
    def do_specific_validation(self, tx: ConfirmationTransaction):
        print("Confirmation")
        return TxValidator.ConfirmationValidator(). \
            validate(tx)

    @dispatch(UnlockingDepositTransaction)
    def do_specific_validation(self, tx: UnlockingDepositTransaction):
        print("Unlocking")
        return TxValidator.DepositUnlockValidator(). \
            validate(tx)

    @dispatch(MintingTransaction)
    def do_specific_validation(self, tx: MintingTransaction):
        print("Minting")
        return TxValidator.MintingTransactionValidator(). \
            validate(tx)

    class OfferValidator(Validator):
        def check_does_not_use_fees_as_inputs(self):
            pass

    class AcceptanceValidator(Validator):
        def check_does_not_use_fees_as_inputs(self):
            pass

    class ConfirmationValidator(Validator):
        def check_uses_fees_inputs_from_the_right_exchange(self):
            pass

    class DepositUnlockValidator(Validator):
        pass

    class MatchTransactionValidator(Validator):
        pass

    class MintingTransactionValidator(Validator):
        pass

    class BaseTxValidator(Validator):

        @staticmethod
        def prepare(obj):
            return {'tx': obj}

        def check_does_not_use_fees_as_inputs(self, tx):
            pass
