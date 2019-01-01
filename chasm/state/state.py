import queue

from depq import DEPQ

from chasm.consensus.primitives.block import Block
from chasm.consensus.primitives.transaction import Transaction
from chasm.state._db import DB


class State:

    def __init__(self, db_dir="~/.xpeer/db"):
        self.utxos = {}
        self.blocks = {}
        self.pending_txs = DEPQ(maxlen=10)  # TODO: configurable size
        self.db = DB(db_dir)

        self.__restore_state()

    def apply_block(self, block: Block):
        pass

    def add_pending_tx(self, tx: Transaction, priority=0):
        self.db.put_pending_tx(tx, priority)
        self.pending_txs.insert(tx, priority)

    def pop_pending_tx(self) -> Transaction:
        try:
            tx, _ = self.pending_txs.popfirst()
            self.db.delete_pending(tx.hash())
            return tx
        except IndexError:
            raise queue.Empty

    def get_utxo(self, block_no: int, index: int):
        return self.utxos[(block_no, index)]

    def get_balance(self, account):
        pass

    def get_transaction(self, tx_hash):
        pass

    def get_block_by_no(self, block_no):
        pass

    def get_block_by_hash(self, block_hash):
        pass

    def __restore_state(self):
        for priority, tx in self.db.get_pending_txs():
            self.add_pending_tx(tx, priority)


# state = State()
