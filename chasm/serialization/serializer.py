import rlp
from rlp import sedes
from rlp.sedes import big_endian_int

from chasm.serialization import countable_list, type_register


class Serializer:
    @classmethod
    def encode(cls, obj) -> bytes:
        type_id = next(type_id for (type_name, type_id) in type_register if type_name == obj.__class__)
        return rlp.encode([type_id, rlp.encode(obj.serialize())])

    @classmethod
    def decode(cls, encoded: bytes) -> [object]:
        [type_id, serialized] = rlp.decode(encoded, sedes.List([big_endian_int, sedes.raw]))
        obj_type = next(type_name for (type_name, id) in type_register if id == type_id)

        sedes_list = []
        for (_field, field_type) in obj_type.__fields__():
            sedes_list.append(field_type)

        decoded = rlp.decode(serialized, sedes.List(sedes_list))

        values = []
        for ((_field, field_type), value) in zip(obj_type.__fields__(), decoded):
            if field_type == sedes.raw:
                value = Serializer.decode(value)
            elif field_type == countable_list:
                value = [Serializer.decode(v) for v in value]
            elif isinstance(field_type, sedes.CountableList):
                value = list(value)
            values.append(value)

        return obj_type.build(values)
