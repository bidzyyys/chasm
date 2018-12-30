from functools import reduce

from ecdsa import SigningKey, VerifyingKey
from rlp import sedes

from chasm import consensus
from chasm.consensus.exceptions import InputOutputSumsException
from chasm.serialization import countable_list
from chasm.serialization import type_register
from chasm.serialization.serializable import Serializable
from chasm.serialization.serializer import Serializer


class Transaction(Serializable):

    @classmethod
    def __fields__(cls) -> [(str, object)]:
        return [('inputs', countable_list), ('outputs', countable_list)]

    def __init__(self, inputs=[], outputs=[]):
        self.inputs = inputs
        self.outputs = outputs
        self.utxos = []

    def find_utxos(self):
        pass

    def sign(self, private_key: str):
        encoded = Serializer.encode(self)
        key = SigningKey.from_string(private_key, curve=consensus.CURVE)
        return key.sign(encoded, hashfunc=consensus.HASH_FUNC)

    def verify_signature(self, public_key, signature):
        encoded = Serializer.encode(self)
        key = VerifyingKey.from_string(public_key, curve=consensus.CURVE, hashfunc=consensus.HASH_FUNC)
        return key.verify(signature, encoded)

    def verify_sums(self):
        input_sums = reduce(lambda partial_sum, utxo: partial_sum + utxo.value, self.utxos, 0)
        output_sums = reduce(lambda partial_sum, output: partial_sum + output.value, self.outputs, 0)
        if input_sums < output_sums:
            raise InputOutputSumsException(self.hash(), input_sums, output_sums)
        else:
            return True

    def hash(self):
        return consensus.HASH_FUNC(Serializer.encode(self)).digest()


class MintingTransaction(Transaction):
    @classmethod
    def __fields__(cls):
        return [('outputs', countable_list)]

    def __init__(self, outputs=[]):
        super().__init__(outputs=outputs)


class OfferTransaction(Transaction):
    @classmethod
    def __fields__(cls):
        fields = [('token_in', sedes.big_endian_int), ('token_out', sedes.big_endian_int),
                  ('value_in', sedes.big_endian_int), ('value_out', sedes.big_endian_int),
                  ('address_out', sedes.binary), ('timeout', sedes.big_endian_int), ('nonce', sedes.big_endian_int),
                  ('confirmation_fee', sedes.big_endian_int), ('deposit', sedes.big_endian_int)]

        return fields + super().__fields__()

    def __init__(self, inputs=None, outputs=None, token_in=None, token_out=None, value_in=None, value_out=None,
                 address_out=None, confirmation_fee=0, deposit=1, nonce=0, timeout=0):

        self.token_in = token_in
        self.token_out = token_out
        self.value_in = value_in
        self.value_out = value_out
        self.address_out = address_out
        self.confirmation_fee = confirmation_fee
        self.deposit = deposit
        self.nonce = nonce
        self.timeout = timeout

        if inputs is None:
            inputs = []
        if outputs is None:
            outputs = []

        super().__init__(inputs=inputs, outputs=outputs)


class SignedTransaction(Serializable):

    @classmethod
    def __fields__(cls) -> [(str, object)]:
        return [('transaction', sedes.raw), ('signatures', sedes.CountableList(sedes.binary))]

    @classmethod
    def build_signed(cls, transaction, private_keys):
        signatures = [transaction.sign(key) for key in private_keys]
        return SignedTransaction(transaction, signatures)

    def __init__(self, transaction=None, signatures=None):
        if signatures is None:
            signatures = []
        self.transaction = transaction
        self.signatures = signatures


type_register.append((Transaction, 3))
type_register.append((SignedTransaction, 4))
type_register.append((MintingTransaction, 5))
type_register.append((OfferTransaction, 6))
