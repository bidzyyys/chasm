from rlp.sedes import big_endian_int, binary

from chasm.serialization import type_registry
from chasm.serialization.serializable import Serializable


class TransferOutput(Serializable):

    @classmethod
    def __fields__(cls) -> [(str, object)]:
        return [('value', big_endian_int), ('receiver', binary)]

    def __init__(self, value: int = 0, receiver: bytes = None):
        self.value = value
        self.receiver = receiver


class XpeerOutput(Serializable):
    @classmethod
    def __fields__(cls) -> [(str, object)]:
        return [('value', big_endian_int), ('receiver', binary), ('exchange', binary)]

    def __init__(self, value: int, receiver: bytes, exchange: bytes):
        self.value = value
        self.receiver = receiver
        self.exchange = exchange


class XpeerFeeOutput(Serializable):
    @classmethod
    def __fields__(cls) -> [(str, object)]:
        return [('value', big_endian_int)]

    def __init__(self, value):
        self.value = value


type_registry.append((TransferOutput, 1))
type_registry.append((XpeerOutput, 2))
type_registry.append((XpeerFeeOutput, 3))
