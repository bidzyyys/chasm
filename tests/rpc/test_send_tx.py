# pylint: disable=missing-docstring
from pytest_bdd import scenario, given, when, then

from chasm.rpc import client
from chasm.rpc.client import send_tx
from . import mock_acceptance, sleep_for_block, init_address


@scenario('test_send_tx.feature', 'Send signed transaction')
def test_send_tx():
    pass


@given('Transaction with its signature')
def parameters(chasm_server, alice_account, bob_account, build_tx, rlp_serializer):
    signing_key, sender = alice_account
    _, receiver = bob_account
    init_address(sender, 20, 1)
    sleep_for_block()
    tx = build_tx(sender, receiver)

    return {
        "tx": tx.encoded.hex(),
        "signature": tx.sign(signing_key.to_string()).hex()
    }


@when('I send transaction with its signature')
def send(parameters, node, test_port):
    client.input = mock_acceptance
    result = send_tx(node=node, port=test_port,
                     tx_hex=parameters["tx"],
                     signatures_hex=[parameters["signature"]])
    parameters["result"] = result
    sleep_for_block()


@then('I get acceptance')
def verify_result(parameters):
    assert parameters["result"]
