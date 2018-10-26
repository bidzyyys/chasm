class Transaction:
    class Output:
        def __init__(self):
            self.value: int

    class XpeerOutput:
        def __init__(self):
            self.offer_hash: bytes
            self.sender: bytes
            self.receiver: bytes
            self.timestamp: int

    class TransferOutput:
        def __init__(self):
            self.receiver: bytes

    class Input:
        def __init__(self):
            self.tx_hash: bytes
            self.index: int
            self.signature: bytes[64]
            self.utxo: Transaction.Output

    def __init__(self):
        self.inputs: [Transaction.Input] = []
        self.outputs: [Transaction.Output] = []
        self.bytes: bytes = bytes
