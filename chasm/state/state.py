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
from chasm.consensus.primitives.transaction import SignedTransaction, MintingTransaction, OfferTransaction, \
    MatchTransaction, UnlockingDepositTransaction, ConfirmationTransaction
from chasm.consensus.validation.block_validator import BlockValidator
from chasm.consensus.validation.tx_validator import TxValidator
from chasm.maintenance.exceptions import TxOverwriteError
from chasm.state._db import DB


class State:
    def __init__(self, db_dir, pending_queue_size):
        self.blocks = {}
        self.tx_indices = {}
        self.utxos = {}
        self.dutxos = {}
        self.blocks_by_height = {}
        self.pending_txs = None
        self.active_offers = {}
        self.matched_offers = {}
        self.current_height = 0
        self.buffer_len = pending_queue_size

        self.block_validator: BlockValidator = None
        self.tx_validator: TxValidator = None

        self._lock = RLock()

        self.db = None
        self._db_dir = db_dir

        try:
            self.db = DB(self._db_dir)
        except plyvel.Error:
            os.makedirs(self._db_dir, exist_ok=True)
            self.db = DB(self._db_dir, create_if_missing=True)
            self._init_database()

        self.reload()

    def apply_block(self, block: Block):
        block_hash = block.hash()

        with _DBTransaction(self), self._lock:
            self._clean_timeouted_offers()

            self._build_tx_indices(block, block_hash)

            new_utxos, new_dutxos = self._extract_outputs_from_block(block)
            self._apply_new_utxos(new_utxos)
            self._apply_new_dutxos(new_dutxos)

            spent_txos = self._extract_inputs_from_block(block)
            self._apply_used_utxos(spent_txos)

            new_offers = self._extract_new_offers(block)
            self._apply_new_offers(new_offers)

            new_matches = self._extract_matched_offers(block)
            self._apply_new_matches(new_matches, block.timestamp)

            confirmations, unlocks = self._extract_deposits_unlocks(block)
            self._apply_unlocked_utxos(confirmations, unlocks)

            self._apply_block(block, block_hash)

    def add_pending_tx(self, tx: SignedTransaction, priority=0):
        with self._lock:
            index = self.pending_txs.push(tx, priority)
            self.db.put_pending_tx(index, tx, priority)

    def pop_pending_tx(self) -> SignedTransaction:
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
            self._clean_timeouted_offers()
            return copy.deepcopy(self.active_offers)

    def get_matched_offers(self):
        with self._lock:
            return copy.deepcopy(self.matched_offers)

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

            self.active_offers = dict(self.db.get_active_offers())
            self.matched_offers = dict(self.db.get_matched_offers())

            self.pending_txs = _PendingTxsQueue(maxlen=self.buffer_len, elements=self.db.get_pending_txs())
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
                if isinstance(tx.transaction, (OfferTransaction, MatchTransaction, UnlockingDepositTransaction)):
                    index = tx.transaction.deposit_index
                    dutxos.append(utxos.pop(-len(tx.outputs) + index))

        return utxos, dutxos

    @staticmethod
    def _extract_new_offers(block):
        return [tx.transaction for tx in block.transactions if
                isinstance(tx, SignedTransaction) and isinstance(tx.transaction, OfferTransaction)]

    @staticmethod
    def _extract_matched_offers(block):
        return [tx.transaction for tx in block.transactions if
                isinstance(tx, SignedTransaction) and isinstance(tx.transaction, MatchTransaction)]

    @staticmethod
    def _extract_deposits_unlocks(block):
        confirmations = [tx.transaction for tx in block.transactions
                         if isinstance(tx, SignedTransaction) and isinstance(tx.transaction, ConfirmationTransaction)]

        unlocks = [tx.transaction for tx in block.transactions
                   if isinstance(tx, SignedTransaction) and isinstance(tx.transaction, UnlockingDepositTransaction)]

        return confirmations, unlocks

    def _apply_block(self, block, block_hash):
        self.blocks[block_hash] = block
        self.blocks_by_height[self.current_height + 1] = block_hash
        self.db.put_block(block, self.current_height + 1)
        self._set_current_height(self.current_height + 1)

    def _apply_new_utxos(self, utxos):
        for (tx_hash, index, output) in utxos:
            self.utxos[(tx_hash, index)] = output
            self.db.put_utxo(tx_hash, index, output)

    def _apply_new_dutxos(self, dutxos):
        for (tx_hash, index, output) in dutxos:
            self.dutxos[(tx_hash, index)] = output
            self.db.put_dutxo(tx_hash, index, output)

    def _apply_used_utxos(self, spend_txos):
        for txo in spend_txos:
            self.utxos.pop(txo)
            self.db.delete_utxo(*txo)

    def _apply_new_offers(self, offers):
        for tx in offers:
            # NOTE: we do not check against overwriting as it is checked when adding to txs indices
            self.active_offers[tx.hash()] = tx
            self.db.put_active_offer(tx)

    def _apply_new_matches(self, matches, block_timestamp):
        for match in matches:
            offer = self.active_offers.pop(match.exchange)
            self.db.delete_active_offer(offer.hash())

            self.matched_offers[offer.hash()] = (offer, match, block_timestamp)
            self.db.put_matched_offer(offer.hash(), offer, match, block_timestamp)

    def _apply_unlocked_utxos(self, confirmations, unlocks):
        for tx in confirmations:
            (offer, acceptance, _timestamp) = self.matched_offers.pop(tx.exchange)
            self.db.delete_matched_offer(tx.exchange)

            utxo1 = (offer.hash(), offer.deposit_index)
            utxo2 = (acceptance.hash(), acceptance.deposit_index)

            dutxo1 = self.dutxos.pop(utxo1)
            self.db.delete_dutxo(*utxo1)

            dutxo2 = self.dutxos.pop(utxo2)
            self.db.delete_dutxo(*utxo2)

            self.utxos[utxo1] = dutxo1
            self.db.put_utxo(*utxo1, output=dutxo1)

            self.utxos[utxo2] = dutxo2
            self.db.put_utxo(*utxo2, output=dutxo2)

        for tx in unlocks:
            (offer, acceptance, _timestamp) = self.matched_offers.pop(tx.exchange)
            self.db.delete_matched_offer(tx.exchange)

            utxo1 = (offer.hash(), offer.deposit_index)
            utxo2 = (acceptance.hash(), acceptance.deposit_index)

            dutxo1 = self.dutxos.pop(utxo1)
            self.db.delete_dutxo(*utxo1)

            dutxo2 = self.dutxos.pop(utxo2)
            self.db.delete_dutxo(*utxo2)

            if tx.proof_side == 0:
                self.utxos[utxo1] = dutxo1
                self.db.put_utxo(*utxo1, output=dutxo1)
            else:
                self.utxos[utxo2] = dutxo2
                self.db.put_utxo(*utxo2, output=dutxo2)

    def _clean_timeouted_offers(self):
        pass

    def _build_tx_indices(self, block, block_hash):

        for tx, i in zip(block.transactions, range(len(block.transactions))):
            if tx.hash() in self.tx_indices:
                raise TxOverwriteError(tx.hash())
            self.tx_indices[tx.hash()] = (block_hash, i)


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


class _DBTransaction:
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
