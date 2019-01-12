import time
from typing import Union

import rlp
from merkletools import MerkleTools
from rlp import sedes

from chasm import consensus
from chasm.consensus.primitives.transaction import MintingTransaction, SignedTransaction
from chasm.serialization import countable_list
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

        def adjust_timestamp(self):
            self.timestamp = int(time.time())

        def set_nonce(self, value):
            self.nonce = value

        def hash(self):
            encoded = rlp.encode(
                [self.previous_block_hash, self.merkle_root, self.timestamp, self.nonce, self.difficulty])
            return consensus.HASH_FUNC(encoded).digest()

    def __init__(self, previous_block_hash, difficulty, merkle_root=None, timestamp=None, nonce=0,
                 transactions: [Union[SignedTransaction, MintingTransaction]] = None):
        if timestamp is None:
            timestamp = int(time.time())
        self._header = Block.Header(previous_block_hash, merkle_root, difficulty, nonce, timestamp)

        self.transactions = transactions if transactions is not None else []

        self._block_height = None

    def update_merkle_root(self):
        merkle_tree = MerkleTools(consensus.HASH_FUNC_NAME)
        txs = [tx.hash().hex() for tx in self.transactions]

        merkle_tree.add_leaf(values=txs)
        merkle_tree.make_tree()

        root = bytes.fromhex(merkle_tree.get_merkle_root())  # the library returns hex encoded hash, but we use bytes
        self._header.merkle_root = root

    def add_transaction(self, tx):
        self.transactions.append(tx)

    @property
    def header(self):
        return self._header

    @property
    def previous_block_hash(self):
        return self._header.previous_block_hash

    @property
    def merkle_root(self):
        return self._header.merkle_root

    @property
    def difficulty(self):
        return self._header.difficulty

    @property
    def timestamp(self):
        return self._header.timestamp

    @property
    def nonce(self):
        return self._header.nonce

    def hash(self):
        return self._header.hash()
