from pytest import mark


from chasm.serialization.json_serializer import JSONSerializer
from chasm.serialization.rlp_serializer import RLPSerializer


@mark.parametrize('serializer', [RLPSerializer(), JSONSerializer()])
def test_encode_input(tx_input, serializer):
    encoded = serializer.encode(tx_input)
    decoded = serializer.decode(encoded)
    assert decoded == tx_input


@mark.parametrize('serializer', [RLPSerializer(), JSONSerializer()])
def test_encode_transfer_output(tx_transfer_output, serializer):
    encoded = serializer.encode(tx_transfer_output)
    decoded = serializer.decode(encoded)
    assert decoded == tx_transfer_output


@mark.parametrize('serializer', [RLPSerializer(), JSONSerializer()])
def test_encode_xpeer_output(tx_xpeer_output, serializer):
    encoded = serializer.encode(tx_xpeer_output)
    decoded = serializer.decode(encoded)
    assert decoded == tx_xpeer_output


@mark.parametrize('serializer', [RLPSerializer(), JSONSerializer()])
def test_encode_xpeer_fee_output(tx_xpeer_fee_output, serializer):
    encoded = serializer.encode(tx_xpeer_fee_output)
    decoded = serializer.decode(encoded)
    assert decoded == tx_xpeer_fee_output


@mark.parametrize('serializer', [RLPSerializer(), JSONSerializer()])
def test_encode_transfer_transaction(transfer_transaction, serializer):
    encoded = serializer.encode(transfer_transaction)
    decoded = serializer.decode(encoded)
    assert decoded == transfer_transaction


@mark.parametrize('serializer', [RLPSerializer(), JSONSerializer()])
def test_encode_signed_transaction(signed_simple_transaction, serializer):
    encoded = serializer.encode(signed_simple_transaction)
    decoded = serializer.decode(encoded)
    assert decoded == signed_simple_transaction


@mark.parametrize('serializer', [RLPSerializer(), JSONSerializer()])
def test_encode_minting_transaction(minting_transaction, serializer):
    encoded = serializer.encode(minting_transaction)
    decoded = serializer.decode(encoded)
    assert decoded == minting_transaction


@mark.parametrize('serializer', [RLPSerializer(), JSONSerializer()])
def test_encode_offer_transaction(xpeer_offer_transaction, serializer):
    encoded = serializer.encode(xpeer_offer_transaction)
    decoded = serializer.decode(encoded)
    assert decoded == xpeer_offer_transaction


@mark.parametrize('serializer', [RLPSerializer(), JSONSerializer()])
def test_encode_match_transaction(xpeer_match_transaction, serializer):
    encoded = serializer.encode(xpeer_match_transaction)
    decoded = serializer.decode(encoded)
    assert decoded == xpeer_match_transaction


@mark.parametrize('serializer', [RLPSerializer(), JSONSerializer()])
def test_encode_confirmation_transaction(xpeer_confirmation_transaction, serializer):
    encoded = serializer.encode(xpeer_confirmation_transaction)
    decoded = serializer.decode(encoded)
    assert decoded == xpeer_confirmation_transaction


@mark.parametrize('serializer', [RLPSerializer(), JSONSerializer()])
def test_encode_deposit_unlocking_transaction(xpeer_deposit_unlocking_transaction, serializer):
    encoded = serializer.encode(xpeer_deposit_unlocking_transaction)
    decoded = serializer.decode(encoded)
    assert decoded == xpeer_deposit_unlocking_transaction


@mark.parametrize('serializer', [RLPSerializer(), JSONSerializer()])
def test_encode_block(block, serializer):
    encoded = serializer.encode(block)
    decoded = serializer.decode(encoded)
    assert decoded == block
