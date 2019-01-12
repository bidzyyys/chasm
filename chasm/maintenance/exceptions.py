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
