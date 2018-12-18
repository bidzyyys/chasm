from typing import List

from chasm.primitives.transaction.tx_input import TxInput


class Transaction:
    def __init__(self):
        self.inputs: List[TxInput] = []
        # self.outputs: List[] = []
