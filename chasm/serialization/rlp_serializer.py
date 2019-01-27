import rlp
from rlp import sedes
from rlp.sedes import big_endian_int

from chasm.serialization import type_registry, countable_list
from chasm.serialization.serializer import Serializer


class RLPSerializer(Serializer):
    def encode(self, obj) -> bytes:
        return self._do_encode(obj.serialize())

    def decode(self, encoded: bytes) -> object:
        [obj_type_id, serialized] = rlp.decode(encoded, sedes.List([big_endian_int, sedes.raw]))
        obj_type = next(type_name for (type_name, type_id) in type_registry if type_id == obj_type_id)

        sedes_list = []
        for (_field, field_type) in obj_type.fields():
            sedes_list.append(field_type)

        decoded = rlp.decode(serialized, sedes.List(sedes_list))

        values = []
        for ((_field, field_type), value) in zip(obj_type.fields(), decoded):
            if field_type == sedes.raw:
                value = self.decode(value)
            elif field_type == countable_list:
                value = [self.decode(v) for v in value]
            elif isinstance(field_type, sedes.CountableList):
                value = list(value)
            values.append(value)

        params = {field: value for ((field, _), value) in zip(obj_type.fields(), values)}

        return obj_type(**params)

    def _do_encode(self, serialized):
        obj_class, *serialized = serialized

        values = []
        for ((field_name, field_type), value) in zip(obj_class.fields(), serialized):
            if field_type == sedes.raw:
                value = self._do_encode(value)
            elif field_type == countable_list:
                value = [self._do_encode(v) for v in value]
            values.append(value)

        type_id = next(type_id for (type_name, type_id) in type_registry if type_name == obj_class)

        return rlp.encode([type_id, rlp.encode(values)])
