from functools import reduce

from ecdsa import SigningKey, VerifyingKey, BadSignatureError
from rlp import sedes

from chasm import consensus
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

    def sign(self, private_key: str):
        encoded = Serializer.encode(self)
        key = SigningKey.from_string(private_key, curve=consensus.CURVE)
        return key.sign(encoded, hashfunc=consensus.HASH_FUNC)

    def verify_signature(self, public_key, signature):
        encoded = Serializer.encode(self)
        key = VerifyingKey.from_string(public_key, curve=consensus.CURVE, hashfunc=consensus.HASH_FUNC)
        try:
            return key.verify(signature, encoded)
        except BadSignatureError:
            return False

    def verify_sums(self, utxos: dict):
        input_sum = reduce(lambda partial_sum, input: partial_sum + utxos.get(input).value, self.inputs, 0)
        output_sum = reduce(lambda partial_sum, output: partial_sum + output.value, self.outputs, 0)
        return input_sum > output_sum


class SignedTransaction(Serializable):

    @classmethod
    def __fields__(cls) -> [(str, object)]:
        return [('transaction', sedes.raw), ('signatures', sedes.CountableList(sedes.binary))]

    def __init__(self, transaction=None, signatures=None):
        if signatures is None:
            signatures = []
        self.transaction = transaction
        self.signatures = signatures


type_register.append((Transaction, 3))
type_register.append((SignedTransaction, 4))
