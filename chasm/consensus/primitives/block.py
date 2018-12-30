class Block:
    MAX_BLOCK_SIZE = 2 ** 20  # 1MB

    class Header:
        def __init__(self, hash_previous_block: bytes, timestamp, merkle_root):
            self.hash_previous_block = hash_previous_block
            self.hash_merkle_root = merkle_root
            self.timestamp = timestamp
            self.nonce = 0
        #
        # def __init__(self, previous_block_hash: bytes):
        #     self.header = self.Header(previous_block_hash)
        #     self.block_hash = bytes(32)
        #     self.block_height = 0
        #     self.transactions: List[transaction]
