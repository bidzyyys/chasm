from enum import Enum
from typing import Union

import plyvel
import rlp
from plyvel._plyvel import WriteBatch
from rlp import sedes

from chasm.consensus import Block
from chasm.serialization.rlp_serializer import RLPSerializer
from chasm.serialization.serializer import Serializer


class DB:
    class _KeyPrefixes(Enum):
        BLOCK = b'b'

        TRANSACTION = b't'
        PENDING_TRANSACTION = b'p'

        UTXO = b'u'
        DUTXO = b'd'

        OFFER_ACTIVE = b'oa'
        OFFER_MATCHED = b'om'


    _rlp_serializer = RLPSerializer()

    def __init__(self, db_dir, create_if_missing=False):
        self.db = plyvel.DB(db_dir, create_if_missing=create_if_missing)

        self.write_obj = self.db

    def start_transaction(self):
        """
        Starts a transaction, writes and deletions from now on will not be executed
        until :func: `execute_transaction` method is invoked.
        """

        if self.write_obj == self.db:
            self.write_obj = self.db.write_batch()
        else:
            raise RuntimeError("Transaction has already been started")

    def execute_transaction(self):
        """
        Executes all the puts and deletions since last `start_transaction`, unless `dismiss_transaction` was invoked.
        """

        if isinstance(self.write_obj, WriteBatch):
            self.write_obj.write()
            self.write_obj = self.db
        else:
            raise RuntimeError("No transaction has been started")

    def dismiss_transaction(self):
        """
        Clears the current transactions and sets to non-transactional mode.
        """
        if isinstance(self.write_obj, WriteBatch):
            self.write_obj.clear()
        self.write_obj = self.db

    def get(self, key, prefix: Union[bytes, _KeyPrefixes] = None):
        if prefix is not None:
            if isinstance(prefix, DB._KeyPrefixes):
                prefix = prefix.value
            key = prefix + key

        return self.db.get(key)

    def put(self, key: bytes, value: bytes, prefix: Union[bytes, _KeyPrefixes] = None):
        if prefix is not None:
            if isinstance(prefix, DB._KeyPrefixes):
                prefix = prefix.value
            key = prefix + key

        self.write_obj.put(key, value)

    def delete(self, key: bytes, prefix: Union[bytes, _KeyPrefixes] = None):
        if prefix is not None:
            if isinstance(prefix, DB._KeyPrefixes):
                prefix = prefix.value
            key = prefix + key

        self.write_obj.delete(key)

    def put_block(self, block: Block, height: int):
        """
        Inserts a block to db.

        NOTE: does no validation
        :param block: Block object
        :param height: block height
        """
        encoded = rlp.encode([height, DB._rlp_serializer.encode(block)],
                             sedes=sedes.List([sedes.big_endian_int, sedes.raw]))
        self.put(block.hash(), encoded, prefix=DB._KeyPrefixes.BLOCK)

    def get_blocks(self):
        """
        Reads db and returns blocks with its heights

        :return: list of (height, block) tuples
        """
        blocks_db = self.db.prefixed_db(DB._KeyPrefixes.BLOCK.value)
        enc = [rlp.decode(value, sedes=sedes.List([sedes.big_endian_int, sedes.raw])) for _, value in blocks_db]
        return [(height, DB._rlp_serializer.decode(encoded)) for height, encoded in enc]

    def delete_utxo(self, tx_hash, index):
        key = rlp.encode([tx_hash, index])
        self.delete(key, prefix=DB._KeyPrefixes.UTXO)

    def put_utxo(self, tx_hash, index, output):
        key = rlp.encode([tx_hash, index])
        self.put(key, DB._rlp_serializer.encode(output), prefix=DB._KeyPrefixes.UTXO)

    def get_utxos(self):
        """
        Reads db and returns map list of utxos

        :return: list of a ((tx_hash, index), utxo) tuple
        """
        utxos_db = self.db.prefixed_db(DB._KeyPrefixes.UTXO.value)
        return [(rlp.decode(k, sedes.List([sedes.binary, sedes.big_endian_int])), DB._rlp_serializer.decode(v)) for
                k, v in utxos_db]

    def put_dutxo(self, tx_hash, index, output):
        key = rlp.encode([tx_hash, index])
        self.put(key, DB._rlp_serializer.encode(output), prefix=DB._KeyPrefixes.DUTXO)

    def get_dutxos(self):
        dutxos_db = self.db.prefixed_db(DB._KeyPrefixes.DUTXO.value)
        return [(rlp.decode(k, sedes.List([sedes.binary, sedes.big_endian_int])), DB._rlp_serializer.decode(v)) for
                k, v in dutxos_db]

    def delete_dutxo(self, tx_hash, index):
        key = rlp.encode([tx_hash, index])
        self.delete(key, prefix=DB._KeyPrefixes.DUTXO)

    def delete_pending(self, index):
        self.delete(Serializer.int_to_bytes(index), prefix=DB._KeyPrefixes.PENDING_TRANSACTION)

    def put_pending_tx(self, index, tx, priority):
        encoded = rlp.encode([priority, DB._rlp_serializer.encode(tx)])
        self.put(Serializer.int_to_bytes(index), encoded, prefix=DB._KeyPrefixes.PENDING_TRANSACTION)

    def get_pending_txs(self):
        """
        Gets pending transactions from the database

        NOTE: It does not restore FIFO order
        :return: list of a (index, priority, tx) tuple
        """
        pending_txs = self.db.prefixed_db(DB._KeyPrefixes.PENDING_TRANSACTION.value)
        enc = [(Serializer.bytes_to_int(key), encoded) for key, encoded in pending_txs]
        pairs = [(key, rlp.decode(encoded, sedes=sedes.List([sedes.big_endian_int, sedes.raw])))
                 for key, encoded in enc]

        return [(index, priority, DB._rlp_serializer.decode(tx_enc)) for index, (priority, tx_enc) in pairs]

    def put_active_offer(self, offer):
        self.put(offer.hash(), DB._rlp_serializer.encode(offer), DB._KeyPrefixes.OFFER_ACTIVE.value)

    def delete_new_offer(self, offer_hash):
        self.delete(offer_hash, DB._KeyPrefixes.OFFER_ACTIVE.value)

    def get_active_offers(self):
        new_offers = self.db.prefixed_db(DB._KeyPrefixes.OFFER_ACTIVE.value)
        return [(k, DB._rlp_serializer.decode(v)) for k, v in new_offers]

    def close(self):
        self.db.close()

    def is_closed(self):
        return self.db.closed
