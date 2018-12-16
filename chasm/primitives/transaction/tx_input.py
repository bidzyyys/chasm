from rlp.sedes import big_endian_int

from chasm.serialization.serializable import Serializable


class TxInput(Serializable):

    @classmethod
    def __fields__(cls):
        return [
            ('block_no', big_endian_int),
            ('output_no', big_endian_int)
        ]

    def __init__(self, block_no=None, output_no=None):
        self.block_no = block_no
        self.output_no = output_no


