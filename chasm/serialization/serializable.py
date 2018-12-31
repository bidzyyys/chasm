from abc import ABC

from rlp import sedes

from chasm.serialization import countable_list
from chasm.serialization.serializer import Serializer


class Serializable(ABC):

    @classmethod
    def __fields__(cls) -> [(str, object)]:
        raise NotImplementedError

    def serialize(self):
        values = []
        for (field, field_type) in self.__fields__():
            value = self.__getattribute__(field)
            if field_type == sedes.raw:
                value = Serializer.encode(value)
            elif field_type == countable_list:
                value = [Serializer.encode(v) for v in value]
            values.append(value)
        return values

    @classmethod
    def build(cls, values: [object]):
        params = {}
        for ((field, _), value) in zip(cls.__fields__(), values):
            params[field] = value
        return cls(**params)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.__dict__ == other.__dict__
