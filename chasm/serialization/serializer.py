from abc import ABC

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

    def decode(self, encoded) -> object:
        raise NotImplementedError

    def encode(self, obj: Serializable):
        raise NotImplementedError
