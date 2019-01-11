from chasm.consensus.validation.tx_validator import Validator


class BlockValidator(Validator):

    def __init__(self, utxos, dutxos, offers, accepted_offers):
        pass

    @staticmethod
    def prepare(obj):
        return {'block': obj}
