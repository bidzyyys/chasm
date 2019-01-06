import queue

from depq import DEPQ

from chasm.consensus.primitives.block import Block
from chasm.consensus.primitives.transaction import Transaction
from chasm.state._db import DB


class State:
    def __init__(self, db_dir="~/.xpeer/db", max_pending_txs=10):
        self.db = DB(db_dir)

        self.utxos = {}
        self.blocks = {}
        self.pending_txs = self._PendingTxsQueue(maxlen=max_pending_txs, elements=self.db.get_pending_txs())

    def apply_block(self, block: Block):
        pass

    def add_pending_tx(self, tx: Transaction, priority=0):
        index = self.pending_txs.push(tx, priority)
        self.db.put_pending_tx(index, tx, priority)

    def pop_pending_tx(self) -> Transaction:
        index, tx = self.pending_txs.pop()
        self.db.delete_pending(index)
        return tx

    def get_utxos(self):
        pass

    def get_utxo(self, tx_hash: int, index: int):
        return self.utxos[(tx_hash, index)]

    def get_transaction(self, tx_hash):
        pass

    def get_block_by_no(self, block_no):
        pass

    def get_block_by_hash(self, block_hash):
        pass

    def get_active_offers(self):
        pass

    def get_accepted_offers(self):
        pass

    def get_dutxos(self):
        pass
    
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
