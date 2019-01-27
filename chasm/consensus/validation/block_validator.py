from chasm.consensus import Block
from chasm.consensus.validation.tx_validator import Validator
from chasm.maintenance.exceptions import BlockHashError, BlockDifficultyError, BlockSizeError
from chasm.serialization.rlp_serializer import RLPSerializer

EXPECTED_BLOCK_INTERVAL = 5  # time interval between two consecutive blocks

DIFFICULTY_COMPUTATION_INTERVAL = 10  # in blocks

INITIAL_MINTING_VALUE = 10 ** 20
MINTING_VALUE_HALVING_PERIOD = 2 ** 16  # about 4 years

MAX_BLOCK_SIZE = 2 ** 20  # 1MB


def check_block_size(block: Block):
    size = len(RLPSerializer().encode(block))
    if not BlockStatelessValidator.check_block_size(size):
        raise BlockSizeError(size)


class BlockValidator(Validator):

    def __init__(self, utxos, offers, accepted_offers, last_block_header, old_block_header, height, dev=False):
        self._last_block: Block.Header = last_block_header
        self._old_block: Block.Header = old_block_header
        self._height = height

        self._dev = dev

    def prepare(self, obj: Block):
        return {
            'block': obj,
            'header': obj.header
        }

    @staticmethod
    def check_all_transactions(block):
        for tx in block.transactions:
            pass

    def check_block_difficulty(self, header: Block.Header):
        expected = BlockStatelessValidator.get_expected_difficulty(self._height, self._last_block.difficulty,
                                                                   self._old_block.timestamp,
                                                                   self._last_block.timestamp, dev=self._dev)

        if not expected == header.difficulty:
            raise BlockDifficultyError(expected, header.difficulty)

    @staticmethod
    def check_block_hash(header: Block.Header):
        if not BlockStatelessValidator.check_block_hash(header.hash(), header.difficulty):
            raise BlockHashError(header.hash(), header.difficulty)


class BlockStatelessValidator:

    @staticmethod
    def check_block_size(size):
        return size <= MAX_BLOCK_SIZE

    @staticmethod
    def get_minting_value(height):
        no_of_divisions = height // MINTING_VALUE_HALVING_PERIOD
        return INITIAL_MINTING_VALUE // (2 ** no_of_divisions)

    @staticmethod
    def get_expected_difficulty(height, last_diff, old_timestamp, last_timestamp, dev=False):
        if dev:
            return 0

        if height % DIFFICULTY_COMPUTATION_INTERVAL == 0:
            return 16  # TODO: recalculate difficulty
        else:
            return 16

    @staticmethod
    def check_block_hash(block_hash, difficulty):
        for k in range(difficulty // 8):
            if block_hash[k] > 0:
                return False

        if block_hash[difficulty // 8] // (2 ** (8 - (difficulty % 8))) > 0:
            return False

        return True
