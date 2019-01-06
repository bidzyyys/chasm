import hashlib

from rlp.sedes import big_endian_int, binary

from chasm import serialization
from chasm.serialization.serializable import Serializable
from chasm.serialization.serializer import Serializer


class TxInput(Serializable):

    @classmethod
    def fields(cls):
        return [
            ('tx_hash', binary),
            ('output_no', big_endian_int)
        ]

    def __init__(self, tx_hash, output_no):
        self.tx_hash = tx_hash
        self.output_no = output_no

    def __hash__(self):
        hash_obj = hashlib.sha1()
        hash_obj.update(Serializer.encode(self))
        return hash_obj.digest().__hash__()


serialization.type_registry.append((TxInput, 0))
