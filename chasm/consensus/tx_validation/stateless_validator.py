from chasm.primitives.transaction.tx_input import TxInput
from chasm.primitives.transaction.tx_output import TxTransferOutput


class StatelessValidator:

    @classmethod
    def validate_tx(cls, tx):
        cls.__validate_inputs(tx.inputs)
        cls.__validate_outputs(tx.outputs)
        cls.__validate_sums(tx.inputs, tx.outputs)

    @classmethod
    def __validate_inputs(cls, tx_inputs: [TxInput]):
        for tx_input in tx_inputs:
            cls.__validate_input(tx_input)

    @classmethod
    def __validate_input(cls, tx_input: TxInput):
        pass

    @classmethod
    def __validate_outputs(cls, tx_outputs: [TxTransferOutput]):
        for tx_output in tx_outputs:
            cls.__validate_output(tx_output)

    @classmethod
    def __validate_output(cls, tx_output):
        pass

    @classmethod
    def __validate_sums(cls, inputs: [TxInput], outputs: [TxTransferOutput]):
        pass
