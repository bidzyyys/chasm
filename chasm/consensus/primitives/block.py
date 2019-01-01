import time

from rlp import sedes

from chasm.serialization import countable_list, type_registry
from chasm.serialization.serializable import Serializable


class Block(Serializable):
    MAX_BLOCK_SIZE = 2 ** 20  # 1MB

    @classmethod
    def __fields__(cls) -> [(str, object)]:
        return [('previous_block_hash', sedes.binary), ('merkle_root', sedes.binary),
                ('nonce', sedes.big_endian_int), ('difficulty', sedes.big_endian_int),
                ('timestamp', sedes.big_endian_int), ('transactions', countable_list)]

    class Header:
        def __init__(self, previous_block_hash, merkle_root, difficulty, nonce, timestamp):
            self.previous_block_hash = previous_block_hash
            self.merkle_root = merkle_root if merkle_root is not None else b''
            self.timestamp = timestamp
            self.nonce = nonce
            self.difficulty = difficulty

        def __eq__(self, other):
            return self.__class__ == other.__class__ and self.__dict__ == other.__dict__

    def __init__(self, previous_block_hash, merkle_root, difficulty, timestamp=None, nonce=0, transactions=None):
        if timestamp is None:
            timestamp = int(time.time())
        self.header = Block.Header(previous_block_hash, merkle_root, difficulty, nonce, timestamp)
        self.block_height = None
        self.transactions = transactions if transactions is not None else []

    @property
    def previous_block_hash(self):
        return self.header.previous_block_hash

    @property
    def merkle_root(self):
        return self.header.merkle_root

    @property
    def difficulty(self):
        return self.header.difficulty

    @property
    def timestamp(self):
        return self.header.timestamp

    @property
    def nonce(self):
        return self.header.nonce


type_registry.append((Block, 11))
