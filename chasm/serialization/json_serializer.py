from json import JSONEncoder, JSONDecoder

from rlp import sedes
from rlp.sedes import binary

from chasm.serialization import countable_list, type_registry, countable_list_of_binaries
from chasm.serialization.serializable import Serializable
from chasm.serialization.serializer import Serializer


class JSONSerializer(JSONEncoder, Serializer):
    def default(self, obj):
        if isinstance(obj, Serializable):
            return self._do_encode(obj.serialize())
        elif isinstance(obj, bytes):
            return obj.hex()

    def decode(self, encoded) -> object:
        return JSONDecoder(object_hook=JSONSerializer._do_decode).decode(encoded)

    def _do_encode(self, serialized):
        obj_class, *fields = serialized
        d = {'type': obj_class.__name__}
        for ((field_name, field_type), value) in zip(obj_class.fields(), fields):
            if field_type == sedes.raw:
                value = self._do_encode(value)
            elif field_type == countable_list:
                value = [self._do_encode(v) for v in value]
            elif field_type == binary:
                value = value.hex()
            d[field_name] = value
        return d

    @staticmethod
    def _do_decode(json_obj):
        obj_type_name = json_obj.pop('type')
        obj_type = next(type_name for (type_name, _) in type_registry if type_name.__name__ == obj_type_name)

        for (field_name, field_type) in obj_type.fields():
            if field_type == binary:
                json_obj[field_name] = bytes.fromhex(json_obj[field_name])
            elif field_type == countable_list_of_binaries:
                json_obj[field_name] = [bytes.fromhex(v) for v in json_obj[field_name]]

        return obj_type(**json_obj)
