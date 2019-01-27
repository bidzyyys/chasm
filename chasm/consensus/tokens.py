from enum import Enum


class Tokens(Enum):
    XPEER = 1
    BITCOIN = 2
    ETHEREUM = 3


ADDRESS_LENGTH = {
    Tokens.XPEER.value: 64,
    Tokens.BITCOIN.value: 32,
    Tokens.ETHEREUM.value: 20
}
