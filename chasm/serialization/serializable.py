from abc import ABC

from rlp import sedes

from chasm.serialization import countable_list


class Serializable(ABC):

    @classmethod
    def fields(cls) -> [(str, object)]:
        raise NotImplementedError

    def serialize(self):
        serialized = [self.__class__]

        for (field, field_type) in self.fields():
            value = self.__getattribute__(field)
            if field_type == sedes.raw:
                value = value.serialize()
            elif field_type == countable_list:
                value = [v.serialize() for v in value]
            serialized.append(value)

        return serialized

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.__dict__ == other.__dict__
