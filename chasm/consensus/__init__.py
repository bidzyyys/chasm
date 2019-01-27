import hashlib
from enum import Enum

import ecdsa

from chasm.consensus.primitives.block import Block

HASH_FUNC_NAME = 'sha3_256'
HASH_FUNC = getattr(hashlib, HASH_FUNC_NAME)
CURVE = ecdsa.SECP256k1

TX_MAX_SIZE = 2 ** 20  # 1MB
BLOCK_MAX_SIZE = TX_MAX_SIZE

GENESIS_BLOCK = Block(int(0).to_bytes(32, byteorder='big'), 0)


class Side(Enum):
    """
    Side of an exchange
    """
    OFFER_MAKER = 0
    OFFER_TAKER = 1
