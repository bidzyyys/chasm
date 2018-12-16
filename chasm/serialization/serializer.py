import rlp
from rlp import sedes
from rlp.sedes import big_endian_int

from chasm.primitives.transaction.tx_input import TxInput
from chasm.primitives.transaction.tx_output import TxTransferOutput, TxXpeerOutput
from chasm.serialization.serializable import Serializable


class Serializer:
    REGISTER = [
        (TxInput, 0),
        (TxTransferOutput, 1),
        (TxXpeerOutput, 2),
    ]

    @classmethod
    def encode(cls, obj: Serializable) -> bytes:
        type_id = next(type_id for (type_name, type_id) in Serializer.REGISTER if type_name == obj.__class__)
        return rlp.encode([type_id, obj.serialize()])

    @classmethod
    def decode(cls, encoded: bytes) -> [object]:
        [type_id, serialized] = rlp.decode(encoded, sedes.List([big_endian_int, sedes.raw]))
        obj_type = next(type_name for (type_name, id) in Serializer.REGISTER if id == type_id)

        sedes_list = []
        for (_field, field_type) in obj_type.__fields__():
            sedes_list.append(field_type)

        decoded = rlp.decode(rlp.encode(serialized), sedes.List(sedes_list))

        values = []
        for ((_field, field_type), value) in zip(obj_type.__fields__(), decoded):
            if field_type == sedes.raw:
                value = Serializer.decode(rlp.encode(value))
            values.append(value)

        return obj_type.build(values)
