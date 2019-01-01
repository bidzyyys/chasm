import hashlib

import ecdsa

HASH_FUNC_NAME = 'sha3_256'
HASH_FUNC = getattr(hashlib, HASH_FUNC_NAME)
CURVE = ecdsa.SECP256k1

TX_MAX_SIZE = 2 ** 20  # 1MB
BLOCK_MAX_SIZE = TX_MAX_SIZE
