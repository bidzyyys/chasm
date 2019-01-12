from chasm.consensus import Block
from chasm.consensus.validation.tx_validator import Validator
from chasm.maintenance.exceptions import BlockHashError

EXPECTED_BLOCK_INTERVAL = 5  # time interval between two consecutive blocks

DIFFICULTY_COMPUTATION_INTERVAL = 10  # in blocks

INITIAL_MINTING_VALUE = 10 ** 20
MINTING_VALUE_HALVING_PERIOD = 2 ** 16  # about 4 years


class BlockValidator(Validator):

    def __init__(self, utxos, offers, accepted_offers, last_block_header, old_block_header, height):
        self._last_block: Block.Header = last_block_header
        self._old_block: Block.Header = old_block_header
        self._height = height

    def prepare(self, obj: Block):
        return {
            'block': obj,
        }

    def check_block_difficulty(self, header: Block.Header):
        pass

    def check_block_hash(self, header: Block.Header):
        pass


class BlockStatelessValidator:

    @staticmethod
    def get_minting_value(height):
        no_of_divisions = height // MINTING_VALUE_HALVING_PERIOD
        return INITIAL_MINTING_VALUE // (2 ** no_of_divisions)

    @staticmethod
    def get_expected_difficulty(height, last_diff, old_timestamp, last_timestamp):
        if height % DIFFICULTY_COMPUTATION_INTERVAL == 0:
            return last_diff  # TODO: recalculate difficulty
        else:
            return last_diff

    @staticmethod
    def check_block_difficulty(height, last_diff, old_timestamp, last_timestamp):
        pass

    @staticmethod
    def check_block_hash(block_hash, difficulty):
        for i in range(2):
            if block_hash[i] > 0:
                raise BlockHashError