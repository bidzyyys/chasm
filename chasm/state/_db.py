import os

import plyvel
import rlp
from rlp import sedes

from chasm.serialization.rlp_serializer import RLPSerializer


class DB:
    def __init__(self, db_dir):
        db_dir = os.path.expanduser(db_dir)
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

    def put_pending_tx(self, index, tx, priority):
        encoded = rlp.encode([priority, RLPSerializer().encode(tx)])
        self.pending_txs_db.put(self._int_to_bytes(index), encoded)

    def delete_pending(self, index):
        self.pending_txs_db.delete(self._int_to_bytes(index))

    def get_pending_txs(self):
        """
        Gets pending transactions from the database

        NOTE: It does not restore FIFO order
        :return: list of pairs (priority, tx)
        """
        enc = [(self._bytes_to_int(key), encoded) for key, encoded in self.pending_txs_db]
        pairs = [(key, rlp.decode(encoded, sedes=sedes.List([sedes.big_endian_int, sedes.raw])))
                 for key, encoded in enc]

        return [(index, priority, RLPSerializer().decode(tx_enc)) for index, (priority, tx_enc) in pairs]

    def close(self):
        self.db.close()

    @staticmethod
    def _int_to_bytes(i: int):
        return i.to_bytes(i.bit_length() + 7 // 8, byteorder='big', signed=False)

    @staticmethod
    def _bytes_to_int(i):
        return int.from_bytes(i, byteorder='big', signed=False)
