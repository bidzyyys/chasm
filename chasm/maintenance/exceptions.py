class ValidationError(Exception):
    pass


class BlockValidationError(ValidationError):
    pass


class TransactionValidationException(Exception):
    def __init__(self, tx_hash, message):
        super().__init__(f"Transaction ({tx_hash.hex()})validation exception :" + message)


class InputOutputSumsException(TransactionValidationException):
    def __init__(self, tx_hash, input_sum, output_sum):
        super().__init__(tx_hash, f"inputs are of greater value than outputs ({input_sum, output_sum})")


class SignaturesAmountException(TransactionValidationException):
    def __init__(self, tx_hash, inputs_amount, signatures_amount):
        super().__init__(tx_hash, f"insufficient amount of signatures ({inputs_amount, signatures_amount})")


class DuplicatedInput(TransactionValidationException):
    def __init__(self, tx_hash, input_tx_hash, input_output_no):
        super().__init__(tx_hash, f"duplicated input: ({input_tx_hash}, {input_output_no})")


class NonexistentUTXO(TransactionValidationException):
    def __init__(self, tx_hash, input_tx_hash, input_output_no):
        super().__init__(tx_hash, f"nonexistent UTXO: ({input_tx_hash}, {input_output_no})")


class TxOverwriteError(Exception):
    def __init__(self, tx_hash):
        super().__init__(f"Tried to overwrite transaction with hash: {tx_hash}")


class IncorrectPassword(ValueError):
    def __init__(self, message):
        super().__init__(message)


class RPCError(ValueError):
    def __init__(self, message):
        super().__init__(message)


class BlockHashError(BlockValidationError):
    def __init__(self):
        super().__init__()
