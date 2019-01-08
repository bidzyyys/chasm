from functools import reduce

from ecdsa import SigningKey, VerifyingKey
from rlp import sedes

from chasm import consensus
from chasm.exceptions import InputOutputSumsException
from chasm.serialization import countable_list, countable_list_of_binaries
from chasm.serialization.serializable import Serializable


class Transaction(Serializable):

    @classmethod
    def fields(cls) -> [(str, object)]:
        return [('inputs', countable_list), ('outputs', countable_list)]

    def __init__(self, inputs=None, outputs=None):
        from chasm.serialization.rlp_serializer import RLPSerializer

        if outputs is None:
            outputs = []
        if inputs is None:
            inputs = []
        self.inputs = inputs
        self.outputs = outputs

        self.utxos = []
        self.encoded = RLPSerializer().encode(self)

    def find_utxos(self):
        pass

    def sign(self, private_key: str):
        key = SigningKey.from_string(private_key, curve=consensus.CURVE)
        return key.sign(self.encoded, hashfunc=consensus.HASH_FUNC)

    def verify_signature(self, public_key, signature):
        key = VerifyingKey.from_string(public_key, curve=consensus.CURVE, hashfunc=consensus.HASH_FUNC)
        return key.verify(signature, self.encoded)

    def verify_sums(self):
        input_sums = reduce(lambda partial_sum, utxo: partial_sum + utxo.value, self.utxos, 0)
        output_sums = reduce(lambda partial_sum, output: partial_sum + output.value, self.outputs, 0)
        if input_sums < output_sums:
            raise InputOutputSumsException(self.hash(), input_sums, output_sums)
        else:
            return True

    def hash(self):
        return consensus.HASH_FUNC(self.encoded).digest()


class MintingTransaction(Transaction):
    @classmethod
    def fields(cls):
        return [('outputs', countable_list), ('height', sedes.big_endian_int)]

    def __init__(self, outputs, height):
        self.height = height
        super().__init__(outputs=outputs)


class OfferTransaction(Transaction):
    @classmethod
    def fields(cls):
        fields = [('token_in', sedes.big_endian_int), ('token_out', sedes.big_endian_int),
                  ('value_in', sedes.big_endian_int), ('value_out', sedes.big_endian_int),
                  ('address_out', sedes.binary), ('timeout', sedes.big_endian_int),
                  ('confirmation_fee_index', sedes.big_endian_int), ('deposit_index', sedes.big_endian_int)]

        return fields + super().fields()

    def __init__(self, inputs, outputs, token_in, token_out, value_in, value_out, address_out, confirmation_fee_index,
                 deposit_index, timeout):
        self.token_in = token_in
        self.token_out = token_out
        self.value_in = value_in
        self.value_out = value_out
        self.address_out = address_out
        self.confirmation_fee_index = confirmation_fee_index
        self.deposit_index = deposit_index
        self.timeout = timeout

        super().__init__(inputs=inputs, outputs=outputs)


class MatchTransaction(Transaction):
    @classmethod
    def fields(cls):
        fields = [('exchange', sedes.binary), ('confirmation_fee_index', sedes.big_endian_int),
                  ('deposit_index', sedes.big_endian_int), ('address_in', sedes.binary)]

        return fields + super().fields()

    def __init__(self, inputs, outputs, exchange, address_in, confirmation_fee_index=0, deposit_index=1):
        self.exchange = exchange
        self.address_in = address_in
        self.confirmation_fee_index = confirmation_fee_index
        self.deposit_index = deposit_index

        super().__init__(inputs, outputs)


class ConfirmationTransaction(Transaction):

    @classmethod
    def fields(cls) -> [(str, object)]:
        fields = [('exchange', sedes.binary), ('tx_in_proof', sedes.binary), ('tx_out_proof', sedes.binary)]
        return fields + super().fields()

    def __init__(self, inputs, outputs, exchange, tx_in_proof, tx_out_proof):
        self.exchange = exchange
        self.tx_in_proof = tx_in_proof
        self.tx_out_proof = tx_out_proof

        super().__init__(inputs, outputs)


class UnlockingDepositTransaction(Transaction):
    @classmethod
    def fields(cls) -> [(str, object)]:
        fields = [('exchange', sedes.binary), ('proof_side', sedes.big_endian_int), ('tx_proof', sedes.binary),
                  ('deposit_index', sedes.big_endian_int)]
        return fields + super().fields()

    def __init__(self, inputs, outputs, exchange, proof_side, tx_proof, deposit_index=0):
        self.exchange = exchange
        self.proof_side = proof_side
        self.tx_proof = tx_proof
        self.deposit_index = deposit_index
        super().__init__(inputs, outputs)


class SignedTransaction(Serializable):

    @classmethod
    def fields(cls) -> [(str, object)]:
        return [('transaction', sedes.raw), ('signatures', countable_list_of_binaries)]

    @classmethod
    def build_signed(cls, transaction, private_keys):
        signatures = [transaction.sign(key) for key in private_keys]
        return SignedTransaction(transaction, signatures)

    def __init__(self, transaction, signatures):
        self.transaction = transaction
        self.signatures = signatures

    def hash(self):
        from chasm.serialization.rlp_serializer import RLPSerializer
        return consensus.HASH_FUNC(RLPSerializer().encode(self)).digest()

    @property
    def inputs(self):
        return self.transaction.inputs

    @property
    def outputs(self):
        return self.transaction.outputs
