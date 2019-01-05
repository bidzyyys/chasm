from abc import ABC

from chasm.serialization.serializable import Serializable

class Serializer(ABC):

    def decode(self, encoded) -> object:
        raise NotImplementedError

    def encode(self, obj: Serializable):
        raise NotImplementedError
