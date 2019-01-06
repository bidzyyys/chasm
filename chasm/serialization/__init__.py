import rlp

countable_list = rlp.sedes.CountableList(rlp.sedes.raw)
countable_list_of_binaries = rlp.sedes.CountableList(rlp.sedes.binary)

type_registry = []
