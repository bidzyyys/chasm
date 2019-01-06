import time

from merkletools import MerkleTools
from rlp import sedes

from chasm import consensus
from chasm.serialization import countable_list, type_registry
from chasm.serialization.serializable import Serializable


class Block(Serializable):
    MAX_BLOCK_SIZE = 2 ** 20  # 1MB

    @classmethod
    def fields(cls) -> [(str, object)]:
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

    def __init__(self, previous_block_hash, difficulty, merkle_root=None, timestamp=None, nonce=0, transactions=None):
        if timestamp is None:
            timestamp = int(time.time())
        self.__header = Block.Header(previous_block_hash, merkle_root, difficulty, nonce, timestamp)

        self.transactions = transactions if transactions is not None else []

        self.__block_height = None

    def update_merkle_root(self):
        merkle_tree = MerkleTools(consensus.HASH_FUNC_NAME)
        txs = [tx.hash() for tx in self.transactions]
        merkle_tree.add_leaf(values=txs)
        root = bytes.fromhex(merkle_tree.get_merkle_root())  # the library returns hex encoded hash, but we use bytes
        self.__header.merkle_root = root

    def adjust_timestamp(self):
        self.__header.timestamp = int(time.time())

    def adjust_nonce(self):
        self.__header.nonce += 1

    def add_transaction(self, tx):
        self.transactions.append(tx)

    @property
    def previous_block_hash(self):
        return self.__header.previous_block_hash

    @property
    def merkle_root(self):
        return self.__header.merkle_root

    @property
    def difficulty(self):
        return self.__header.difficulty

    @property
    def timestamp(self):
        return self.__header.timestamp

    @property
    def nonce(self):
        return self.__header.nonce


type_registry.append((Block, 11))
