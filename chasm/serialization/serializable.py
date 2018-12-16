from abc import ABC

from rlp import sedes


class Serializable(ABC):

    @classmethod
    def __fields__(cls) -> [(str, object)]:
        raise NotImplementedError

    def serialize(self):
        values = []
        for (field, field_type) in self.__fields__():
            if field_type == sedes.raw:
                field = field.serialize()
            values.append(self.__getattribute__(field))
        return values

    @classmethod
    def build(cls, values: [object]):
        instance = cls()
        for ((field, _), value) in zip(cls.__fields__(), values):
            setattr(instance, field, value)
        return instance

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.__dict__ == other.__dict__
