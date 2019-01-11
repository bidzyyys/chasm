import copy
import os
import queue
from threading import RLock
from typing import Union

import plyvel
import rlp
from depq import DEPQ

from chasm.consensus import GENESIS_BLOCK
from chasm.consensus.primitives.block import Block
from chasm.consensus.primitives.transaction import Transaction, SignedTransaction, MintingTransaction
from chasm.maintenance.exceptions import TxOverwriteError
from chasm.services_manager import Service
from chasm.state._db import DB


class State(Service):
    def __init__(self, db_dir, pending_queue_size):
        self.blocks = {}
        self.tx_indices = {}
        self.utxos = {}
        self.dutxos = {}
        self.blocks_by_height = {}
        self.pending_txs = None
        self.active_offers = {}
        self.accepted_offers = {}
        self.current_height = 0
        self.buffer_len = pending_queue_size

        self._lock = RLock()

        self._db = None
        self._db_dir = db_dir

    def start(self, _stop_condition):

        try:
            self.db = DB(self._db_dir)
        except plyvel.Error:
            os.makedirs(self._db_dir, exist_ok=True)
            self.db = DB(self._db_dir, create_if_missing=True)
            self._init_database()

        self.reload()
        return True

    def stop(self):
        self.close()

    def is_running(self):
        return not self.db.is_closed()

    def apply_block(self, block: Block):
        block_hash = block.hash()

        with self._Transaction(self), self._lock:
            self.blocks[block_hash] = block
            self.blocks_by_height[self.current_height + 1] = block_hash

            for tx, i in zip(block.transactions, range(len(block.transactions))):
                if tx.hash() in self.tx_indices:
                    raise TxOverwriteError(tx.hash())
                self.tx_indices[tx.hash()] = (block_hash, i)

            used_utxos = self._extract_inputs_from_block(block)
            new_utxos, new_dutxos = self._extract_outputs_from_block(block)

            for utxo in used_utxos:
                self.utxos.pop(utxo)
                self.db.delete_utxo(*utxo)

            for (tx_hash, index, output) in new_utxos:
                self.utxos[(tx_hash, index)] = output
                self.db.put_utxo(tx_hash, index, output)

            for (tx_hash, index, output) in new_dutxos:
                self.dutxos[(tx_hash, index)] = output
                self.db.put_dutxo(tx_hash, index, output)

            self.db.put_block(block, self.current_height + 1)
            self._set_current_height(self.current_height + 1)

    def add_pending_tx(self, tx: Transaction, priority=0):
        with self._lock:
            index = self.pending_txs.push(tx, priority)
            self.db.put_pending_tx(index, tx, priority)

    def pop_pending_tx(self) -> Union[SignedTransaction, MintingTransaction]:
        with self._lock:
            index, tx = self.pending_txs.pop()
            self.db.delete_pending(index)

        return tx

    def get_utxos(self) -> dict:
        with self._lock:
            return copy.deepcopy(self.utxos)

    def get_utxo(self, tx_hash: int, index: int) -> Union[SignedTransaction, MintingTransaction]:
        with self._lock:
            utxo = self.utxos[(tx_hash, index)]
            return copy.deepcopy(utxo)

    def get_transaction(self, tx_hash) -> Union[SignedTransaction, MintingTransaction]:
        with self._lock:
            block, index = self.tx_indices[tx_hash]
            block = self.get_block_by_hash(block)
            return block.transactions[index]

    def get_block_by_no(self, block_no) -> Block:
        with self._lock:
            block_hash = self.blocks_by_height[block_no]
            return self.get_block_by_hash(block_hash)

    def get_block_by_hash(self, block_hash):
        with self._lock:
            return copy.deepcopy(self.blocks[block_hash])

    def get_active_offers(self):
        with self._lock:
            return copy.deepcopy(self.active_offers)

    def get_accepted_offers(self):
        with self._lock:
            return copy.deepcopy(self.accepted_offers)

    def get_dutxos(self):
        with self._lock:
            return copy.deepcopy(self.dutxos)

    def _read_current_height(self):
        encoded = self.db.get(b'highest_block')
        return rlp.decode(encoded, rlp.sedes.big_endian_int)

    def _set_current_height(self, height):
        self.current_height = height
        encoded = rlp.encode(height)
        self.db.put(b'highest_block', encoded)

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

    class _Transaction:
        def __init__(self, state):
            self.associated_state = state

        def __enter__(self):
            self.associated_state.db.start_transaction()

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is not None:
                self.associated_state.db.dismiss_transaction()
                self.associated_state.reload()
            else:
                self.associated_state.db.execute_transaction()

    @staticmethod
    def _build_blocks_from_db_data(db_blocks):
        block_indices = {}
        tx_indices = {}
        blocks = {}

        for (height, block) in db_blocks:
            block_hash = block.hash()
            blocks[block_hash] = block
            block_indices[height] = block_hash
            for tx, i in zip(block.transactions, range(len(block.transactions))):
                tx_indices[tx.hash()] = (block_hash, i)

        return blocks, block_indices, tx_indices

    def reload(self):
        with self._lock:
            blocks, blocks_height_indexes, tx_indices = self._build_blocks_from_db_data(self.db.get_blocks())

            self.blocks = blocks
            self.blocks_by_height = blocks_height_indexes

            self.tx_indices = tx_indices

            self.utxos = dict(self.db.get_utxos())
            self.dutxos = dict(self.db.get_dutxos())

            self.pending_txs = self._PendingTxsQueue(maxlen=self.buffer_len, elements=self.db.get_pending_txs())
            self.current_height = self._read_current_height()

    def _init_database(self):
        self.db.put_block(GENESIS_BLOCK, 0)
        self._set_current_height(0)

    @staticmethod
    def _extract_inputs_from_block(block):
        inputs = []

        for tx in block.transactions:
            for tx_input in tx.inputs:
                inputs.append((tx_input.tx_hash, tx_input.output_no))

        return inputs

    @staticmethod
    def _extract_outputs_from_block(block):
        utxos = []
        dutxos = []

        for tx in block.transactions:
            for output, i in zip(tx.outputs, range(tx.outputs.__len__())):
                utxos.append((tx.hash(), i, output))
            if isinstance(tx, SignedTransaction):
                if hasattr(tx.transaction, 'deposit_index'):
                    index = tx.transaction.deposit_index
                    dutxos.append(utxos.pop(-len(tx.outputs) + index))

        return utxos, dutxos
