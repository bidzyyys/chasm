from rlp.sedes import raw, binary, CountableList

# pylint: disable=invalid-name

countable_list = CountableList(raw)
countable_list_of_binaries = CountableList(binary)

type_registry = []
