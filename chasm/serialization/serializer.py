from abc import ABC

import rlp
from rlp import sedes

from chasm.consensus.primitives.block import Block
from chasm.consensus.primitives.transaction import Transaction, \
    SignedTransaction, UnlockingDepositTransaction, MatchTransaction, \
    ConfirmationTransaction, OfferTransaction, MintingTransaction
from chasm.consensus.primitives.tx_input import TxInput
from chasm.consensus.primitives.tx_output import TransferOutput, \
    XpeerFeeOutput, XpeerOutput
from chasm.serialization import type_registry
from chasm.serialization.serializable import Serializable

type_registry.append((TxInput, 0))
type_registry.append((TransferOutput, 1))
type_registry.append((XpeerOutput, 2))
type_registry.append((XpeerFeeOutput, 3))
type_registry.append((Transaction, 4))
type_registry.append((SignedTransaction, 5))
type_registry.append((MintingTransaction, 6))
type_registry.append((OfferTransaction, 7))
type_registry.append((MatchTransaction, 8))
type_registry.append((ConfirmationTransaction, 9))
type_registry.append((UnlockingDepositTransaction, 10))
type_registry.append((Block, 11))


class Serializer(ABC):

    @classmethod
    def int_to_bytes(cls, i: int):
        return rlp.encode(i)

    @classmethod
    def bytes_to_int(cls, b: bytes):
        return rlp.decode(b, sedes.big_endian_int)

    def decode(self, encoded) -> object:
        raise NotImplementedError

    def encode(self, obj: Serializable):
        raise NotImplementedError
