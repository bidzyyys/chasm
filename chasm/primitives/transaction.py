from typing import List
import rlp


class Transaction:
    def __init__(self):
        self.inputs: List[Transaction.Input] = []
        self.outputs: List[Transaction.Output] = []

    def add_input(self, block_no: int, output_no: int):
        self.inputs.append(Transaction.Input(block_no, output_no))
