from rlp.sedes import big_endian_int, binary

from chasm.serialization.serializable import Serializable


class TransferOutput(Serializable):

    @classmethod
    def fields(cls) -> [(str, object)]:
        return [('value', big_endian_int), ('receiver', binary)]

    def __init__(self, value: int, receiver: bytes):
        self.value = value
        self.receiver = receiver


class XpeerOutput(Serializable):
    @classmethod
    def fields(cls) -> [(str, object)]:
        return [('value', big_endian_int), ('receiver', binary), ('sender', binary), ('exchange', binary)]

    def __init__(self, value: int, sender: bytes, receiver: bytes, exchange: bytes):
        self.value = value
        self.sender = sender
        self.receiver = receiver
        self.exchange = exchange


class XpeerFeeOutput(Serializable):
    @classmethod
    def fields(cls) -> [(str, object)]:
        return [('value', big_endian_int)]

    def __init__(self, value):
        self.value = value
