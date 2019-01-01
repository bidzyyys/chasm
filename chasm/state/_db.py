import plyvel
import rlp
from rlp import sedes

from chasm.serialization.serializer import Serializer


class DB:
    def __init__(self, db_dir):
        self.db = plyvel.DB(db_dir, create_if_missing=True)
        self.utxos_db = self.db.prefixed_db(b'u')
        self.transactions_db = self.db.prefixed_db(b't')
        self.blocks_db = self.db.prefixed_db(b'b')
        self.pending_txs_db = self.db.prefixed_db(b'p')

    def get_value(self, key):
        pass

    def get_utxo(self, block_no, index):
        pass

    def get_utxos(self):
        pass

    def delete_utxo(self, block_no, index):
        pass

    def delete_utxos(self, utxos: [((int, int), bytes)]):
        pass

    def put_pending_tx(self, tx, priority):
        encoded = rlp.encode([priority, Serializer.encode(tx)])
        self.pending_txs_db.put(tx.hash(), encoded)

    def delete_pending(self, tx_hash):
        self.pending_txs_db.delete(tx_hash)

    def get_pending_txs(self):
        """
        Gets pending transactions from the database

        NOTE: It does not restore FIFO order
        :return: list of pairs (priority, tx)
        """
        enc = [encoded for _key, encoded in self.pending_txs_db]
        pairs = [rlp.decode(encoded, sedes=sedes.List([sedes.big_endian_int, sedes.raw])) for encoded in enc]
        return [(priority, Serializer.decode(tx_enc)) for priority, tx_enc in pairs]
