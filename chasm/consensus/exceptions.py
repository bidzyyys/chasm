class TransactionValidationException(Exception):
    def __init__(self, tx_hash, message):
        super().__init__(f"Transaction ({tx_hash.hex()})validation exception :" + message)


class InputOutputSumsException(TransactionValidationException):
    def __init__(self, tx_hash, input_sum, output_sum):
        super().__init__(tx_hash, f"inputs are of greater value than outputs ({input_sum, output_sum})")
