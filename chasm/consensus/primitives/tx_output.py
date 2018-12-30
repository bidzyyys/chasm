from rlp.sedes import big_endian_int, binary

from chasm.serialization import type_register
from chasm.serialization.serializable import Serializable


class TxTransferOutput(Serializable):

    @classmethod
    def __fields__(cls) -> [(str, object)]:
        return [('value', big_endian_int), ('receiver', binary)]

    def __init__(self, value: int = 0, receiver: bytes = None):
        self.value = value
        self.receiver = receiver


class TxXpeerOutput(Serializable):
    @classmethod
    def __fields__(cls) -> [(str, object)]:
        return [('value', big_endian_int), ('receiver', binary), ('exchange', binary)]

    def __init__(self, value: int = 0, receiver: bytes = None, exchange: bytes = None):
        self.value = value
        self.receiver = receiver
        self.exchange = exchange


type_register.append((TxTransferOutput, 1))
type_register.append((TxXpeerOutput, 2))
