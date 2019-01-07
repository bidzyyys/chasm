import os

import plyvel
import rlp
from rlp import sedes

from chasm.consensus import Block
from chasm.serialization.rlp_serializer import RLPSerializer


class DB:
    _rlp_serializer = RLPSerializer()

    def __init__(self, db_dir, create_if_missing=False):
        db_dir = os.path.expanduser(db_dir)

        self.db = plyvel.DB(db_dir, create_if_missing=create_if_missing)

        self.utxos_db = self.db.prefixed_db(b'u')
        self.transactions_db = self.db.prefixed_db(b't')
        self.blocks_db = self.db.prefixed_db(b'b')
        self.pending_txs_db = self.db.prefixed_db(b'p')

    def get_value(self, key):
        return self.db.get(key)

    def put_value(self, key, value):
        self.db.put(key, value)

    def put_block(self, block: Block, height: int):
        """
        Inserts a block to db.

        NOTE: does no validation
        :param block: Block object
        :param height: block height
        """
        encoded = rlp.encode([height, DB._rlp_serializer.encode(block)],
                             sedes=sedes.List([sedes.big_endian_int, sedes.raw]))
        self.blocks_db.put(block.hash(), encoded)

    def get_blocks(self):
        """
        Reads db and returns blocks with its heights

        :return: list of (height, block) tuples
        """
        enc = [rlp.decode(value, sedes=sedes.List([sedes.big_endian_int, sedes.raw])) for _, value in self.blocks_db]
        return [(height, DB._rlp_serializer.decode(encoded)) for height, encoded in enc]

    def delete_utxo(self, block_no, index):
        pass

    def get_utxo(self, block_no, index):
        pass

    def get_utxos(self):
        pass

    def delete_pending(self, index):
        self.pending_txs_db.delete(self._int_to_bytes(index))

    def delete_utxos(self, utxos: [((int, int), bytes)]):
        pass

    def put_pending_tx(self, index, tx, priority):
        encoded = rlp.encode([priority, DB._rlp_serializer.encode(tx)])
        self.pending_txs_db.put(self._int_to_bytes(index), encoded)

    def get_pending_txs(self):
        """
        Gets pending transactions from the database

        NOTE: It does not restore FIFO order
        :return: list of pairs (index, priority, tx)
        """
        enc = [(self._bytes_to_int(key), encoded) for key, encoded in self.pending_txs_db]
        pairs = [(key, rlp.decode(encoded, sedes=sedes.List([sedes.big_endian_int, sedes.raw])))
                 for key, encoded in enc]

        return [(index, priority, DB._rlp_serializer.decode(tx_enc)) for index, (priority, tx_enc) in pairs]

    def close(self):
        self.db.close()

    @staticmethod
    def _bytes_to_int(i):
        return rlp.decode(i, sedes.big_endian_int)

    @staticmethod
    def _int_to_bytes(i):
        return rlp.encode(i)
