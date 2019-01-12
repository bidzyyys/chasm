import copy

from chasm.consensus import Block
from chasm.consensus.validation.block_validator import BlockStatelessValidator
from chasm.maintenance.exceptions import BlockHashError


class Miner:
    def __init__(self, header: Block.Header):
        self._header = copy.deepcopy(header)
        self.result = None

    def check_nonce_in_range(self, r: range):
        for i in r:
            self._header.set_nonce(i)
            try:

                BlockStatelessValidator.check_block_hash(self._header.hash(), self._header.difficulty)
                self.result = i
                break
            except BlockHashError:
                pass
