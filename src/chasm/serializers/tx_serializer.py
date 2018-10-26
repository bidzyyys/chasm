from src.chasm.serializers.serializer import Serializer


class TxSerializer(Serializer):

    @staticmethod
    def to_bytes(obj: object):
        return bytes(0)

    @staticmethod
    def from_bytes(b: bytes):
        return object()

