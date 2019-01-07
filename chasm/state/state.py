import copy
import queue

import plyvel
import rlp
from depq import DEPQ

from chasm.consensus import GENESIS_BLOCK
from chasm.consensus.primitives.block import Block
from chasm.consensus.primitives.transaction import Transaction
from chasm.state._db import DB


class State:
    def __init__(self, db_dir="~/.chasm/db", max_pending_txs=10):
        try:
            self.db = DB(db_dir)
        except plyvel.Error:
            self.db = DB(db_dir, create_if_missing=True)
            self._init_database()

        self.utxos = {}

        blocks, blocks_height_indexes = self._build_blocks_from_db_data(self.db.get_blocks())
        self.blocks = blocks
        self.blocks_by_height = blocks_height_indexes

        self.dutxos = {}

        self.pending_txs = self._PendingTxsQueue(maxlen=max_pending_txs, elements=self.db.get_pending_txs())

        self.current_height = self._read_current_height()

    def apply_block(self, block: Block):
        current_block_height = self._read_current_height() + 1
        block_hash = block.hash()

        self.blocks[block_hash] = block
        self.blocks_by_height[current_block_height] = block_hash

        self.db.put_block(block, current_block_height)
        self._set_current_height(current_block_height)

    def add_pending_tx(self, tx: Transaction, priority=0):
        index = self.pending_txs.push(tx, priority)
        self.db.put_pending_tx(index, tx, priority)

    def pop_pending_tx(self) -> Transaction:
        index, tx = self.pending_txs.pop()
        self.db.delete_pending(index)
        return tx

    def get_utxos(self):
        return copy.deepcopy(self.utxos)

    def get_utxo(self, tx_hash: int, index: int):
        utxo = self.utxos[(tx_hash, index)]
        return copy.deepcopy(utxo)

    def get_transaction(self, tx_hash):
        pass

    def get_block_by_no(self, block_no):
        block_hash = self.blocks_by_height[block_no]
        return self.get_block_by_hash(block_hash)

    def get_block_by_hash(self, block_hash):
        return copy.deepcopy(self.blocks[block_hash])

    def get_active_offers(self):
        pass

    def get_accepted_offers(self):
        pass

    def get_dutxos(self):
        return copy.deepcopy(self.dutxos)

    def _read_current_height(self):
        encoded = self.db.get_value(b'highest_block')
        return rlp.decode(encoded, rlp.sedes.big_endian_int)

    def _set_current_height(self, height):
        self.current_height = height
        encoded = rlp.encode(height)
        self.db.put_value(b'highest_block', encoded)

    def close(self):
        self.db.close()

    class _PendingTxsQueue:
        def __init__(self, maxlen, elements=None):
            self.free_indices = queue.Queue(maxsize=maxlen)
            self.priority_queue = DEPQ(maxlen=maxlen)

            indices = [i for i in range(maxlen)]

            if elements is not None:
                for index, priority, tx in elements:
                    indices.remove(index)
                    self.free_indices.put_nowait(index)
                    self.push(tx, priority)

            for i in indices:
                self.free_indices.put_nowait(i)

        def push(self, tx, priority):
            if self.priority_queue.size() == self.priority_queue.maxlen:
                if self.priority_queue.low() < priority:
                    index, _ = self.priority_queue.last()
                    self.free_indices.put_nowait(index)
                else:
                    raise queue.Full

            index = self.free_indices.get_nowait()
            self.priority_queue.insert((index, tx), priority)
            return index

        def pop(self):
            if self.is_empty():
                raise queue.Empty

            (index, tx), _ = self.priority_queue.popfirst()
            self.free_indices.put_nowait(index)

            return index, tx

        def is_empty(self):
            return self.priority_queue.is_empty()

    @staticmethod
    def _build_blocks_from_db_data(db_blocks):
        indexes = {}
        blocks = {}
        for (height, block) in db_blocks:
            block_hash = block.hash()
            blocks[block_hash] = block
            indexes[height] = block_hash

        return blocks, indexes

    def _init_database(self):
        self.db.put_block(GENESIS_BLOCK, 0)
        self._set_current_height(0)
