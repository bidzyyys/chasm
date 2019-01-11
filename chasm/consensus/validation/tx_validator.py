from chasm.consensus.primitives.transaction import Transaction, SignedTransaction
from chasm.consensus.validation.validator import Validator


class TxValidator(Validator):
    def __init__(self, utxos, dutxos, active_offers, accepted_offers):
        self._utxos = utxos
        self._dutxos = dutxos
        self._active_offers = active_offers
        self._accepted_offers = accepted_offers

    @staticmethod
    def prepare(signed_tx: SignedTransaction):
        return {'tx': signed_tx.transaction, 'signatures': signed_tx.signatures}

    def check_size(self, tx):
        pass

    def check_inputs_repetitions(self, tx):
        pass

    def check_outputs(self, tx):
        pass

    def check_sums(self, tx):
        pass

    def check_signatures(self, tx, signatures):
        pass

    def check_inputs_are_utxos(self, tx):
        pass

    def check_type_specifics(self, tx):
        validator = None
        if isinstance(tx, Transaction):
            validator = TxValidator.BaseTxValidator()
        else:
            raise NotImplementedError
        validator.validate(tx)

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

    class BaseTxValidator(Validator):

        @staticmethod
        def prepare(obj):
            return {'tx': obj}

        def check_does_not_use_fees_as_inputs(self, tx):
            pass
