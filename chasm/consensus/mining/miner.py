import copy
import time

from chasm.consensus import Block


class Miner:
    def __init__(self, header: Block.Header):
        self._header = copy.deepcopy(header)
        self._block_validator = None
        self.result = None

    def check_nonce_in_range(self, r: range):
        time.sleep(5)
        self.result = 1
