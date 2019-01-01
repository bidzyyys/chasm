import rlp

countable_list = rlp.sedes.CountableList(rlp.sedes.raw)

type_registry = []
