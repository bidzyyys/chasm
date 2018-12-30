import hashlib

import ecdsa

HASH_FUNC = hashlib.sha3_256
CURVE = ecdsa.SECP256k1

TX_MAX_SIZE = 2 ** 20  # 1MB
BLOCK_MAX_SIZE = TX_MAX_SIZE
