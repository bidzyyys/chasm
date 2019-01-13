class ValidationError(Exception):
    pass


class BlockValidationError(ValidationError):
    pass


class TransactionValidationException(Exception):
    def __init__(self, tx_hash, message):
        super().__init__(f"Transaction ({tx_hash.hex()})validation exception :" + message)


class IncorrectPassword(ValueError):
    def __init__(self, message):
        super().__init__(message)


class RPCError(ValueError):
    def __init__(self, message):
        super().__init__(message)


class BlockHashError(BlockValidationError):
    def __init__(self):
        super().__init__()


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


class TransactionSizeException(TransactionValidationException):
    def __init__(self, tx_hash, size):
        super().__init__(tx_hash, f"too much size: {size} bytes")


class XpeerFeeOutputException(ValueError):
    pass


class XpeerOutputException(ValueError):
    pass


class UseXpeerFeeOutputAsInputException(TransactionValidationException):
    def __init__(self, tx_hash):
        super().__init__(tx_hash, f"transaction use XpeerFeeOutput as input")


class TxOverwriteError(Exception):
    def __init__(self, tx_hash):
        super().__init__(f"Tried to overwrite transaction with hash: {tx_hash}")


class SenderUseXpeerOutputBeforeTimeoutError(TransactionValidationException):
    def __init__(self, tx_hash, exchange):
        super().__init__(tx_hash, f"Sender use XpeerOutput before timeout from exchange: {exchange}")


class SenderUseXpeerOutputAfterConfirmationError(TransactionValidationException):
    def __init__(self, tx_hash, exchange):
        super().__init__(tx_hash, f"Sender use XpeerOutput after confirmation from exchange: {exchange}")


class ReceiverUseXpeerOutputBeforeConfirmationError(TransactionValidationException):
    def __init__(self, tx_hash, exchange):
        super().__init__(tx_hash, f"Receiver use XpeerOutput after confirmation from exchange: {exchange}")


class InvalidAddressLengthOutputError(TransactionValidationException):
    def __init__(self, tx_hash, output_no):
        super().__init__(tx_hash, f"Invalid address length, output_no: {output_no}")


class InvalidAddressLengthPaymentError(TransactionValidationException):
    def __init__(self, tx_hash, length, token):
        super().__init__(tx_hash, f"Invalid address for income, token: {token} length: {length}")


class SendXpeerOutputWithoutExchangeError(TransactionValidationException):
    def __init__(self, tx_hash, output_no):
        super().__init__(tx_hash, f"Try to send XpeerOutput without exchange, output_no: {output_no}")


class SendXpeerFeeOutputError(TransactionValidationException):
    def __init__(self, tx_hash, output_no):
        super().__init__(tx_hash, f"Try to send XpeerFeeOutput, output_no: {output_no}")
class BlockDifficultyError(BlockValidationError):
    def __init__(self, expected, actual):
        super().__init__(f'Expected difficulty {expected}, but got {actual}')


class BlockHashError(BlockValidationError):
    def __init__(self, block_hash: bytes, expected_diff: int):
        super().__init__(f'Expected difficulty {expected_diff}, but got hash: {block_hash.hex()}')


class BlockSizeError(BlockValidationError):
    def __init__(self, actual_size):
        from chasm.consensus.validation.block_validator import MAX_BLOCK_SIZE
        super().__init__(f'Block size {actual_size} (max size={MAX_BLOCK_SIZE})')


class NegativeOutput(TransactionValidationException):
    def __init__(self, tx_hash, output_no):
        super().__init__(tx_hash, f"Try to send negative output, output_no: {output_no}")


class OfferExistsError(TransactionValidationException):
    def __init__(self, tx_hash):
        super().__init__(tx_hash, f"Try to add existing offer")


class MatchNonExistentOfferError(TransactionValidationException):
    def __init__(self, tx_hash, offer_hash):
        super().__init__(tx_hash, f"Try to accept nonexistent offer: {offer_hash.hex()}")


class DepositOutputError(TransactionValidationException):
    def __init__(self, tx_hash, output_no):
        super().__init__(tx_hash, f"Deposit is not a TransferOutput, output_no: {output_no}")


class DepositValueError(TransactionValidationException):
    def __init__(self, tx_hash, index, value, required):
        super().__init__(tx_hash, f"Too small deposit: {value}, required: {required}, output_no: {index}")


class OutputIsNotXpeerFeeOutputError(TransactionValidationException):
    def __init__(self, tx_hash, index):
        super().__init__(tx_hash, f"Confirmation fee is not XpeerFeeOutput, output_no: {index}")


class ConfFeeIndexOutOfRangeError(TransactionValidationException):
    def __init__(self, tx_hash, index):
        super().__init__(tx_hash, f"Confirmation fee index out of range: {index}")


class UnknownExchangeTokenError(TransactionValidationException):
    def __init__(self, tx_hash, token):
        super().__init__(tx_hash, f"Unknown exchange token: {token}")


class ExchangeAmountBelowZeroError(TransactionValidationException):
    def __init__(self, tx_hash, token, amount):
        super().__init__(tx_hash, f"Exchange amount below zero: {amount}, token: {token}")


class OfferTimeoutBeforeNowError(TransactionValidationException):
    def __init__(self, tx_hash, timeout):
        super().__init__(tx_hash, f"Offer timeout before now: {timeout}")


class ConfirmationNotUseXpeerFeeOutputError(TransactionValidationException):
    def __init__(self, tx_hash, input_no):
        super().__init__(tx_hash, f"Confirmation should use only XpeerFeeOutput: input_no: {input_no}")


class ConfirmationUnknownExchangeError(TransactionValidationException):
    def __init__(self, tx_hash, exchange):
        super().__init__(tx_hash, f"Confirmation of unknown exchange: {exchange.hex()}")
