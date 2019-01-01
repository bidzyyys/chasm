import hashlib

from rlp.sedes import big_endian_int

from chasm import serialization
from chasm.serialization.serializable import Serializable
from chasm.serialization.serializer import Serializer


class TxInput(Serializable):

    @classmethod
    def __fields__(cls):
        return [
            ('block_no', big_endian_int),
            ('output_no', big_endian_int)
        ]

    def __init__(self, block_no=None, output_no=None):
        self.block_no = block_no
        self.output_no = output_no

    def __hash__(self):
        hash_obj = hashlib.sha1()
        hash_obj.update(Serializer.encode(self))
        return hash_obj.digest().__hash__()


serialization.type_registry.append((TxInput, 0))
