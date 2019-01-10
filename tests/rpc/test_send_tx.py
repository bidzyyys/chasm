# pylint: disable=missing-docstring
from pytest_bdd import scenario, given, when, then

from chasm.rpc import client
from chasm.rpc.client import send_tx
from . import mock_input_yes, TEST_NODE, TEST_PORT, \
    skip_test

pytestmark = skip_test()


@scenario('test_send_tx.feature', 'Send signed transaction')
def test_send_tx():
    pass


@given('Transaction with its signature')
def parameters():
    return {
        "tx": "f8de04b8dbf8d9cc8bca8088c785546573747345f8cab862f86001b85df85b0ab8583056301006072a8648ce3d020106052b8104000a034200042a86469754777b30bc63304ac057db2882b1a69a81ac57b4dae3490f0df367d7232e81be05d5520742191a5d5254b0be544255ad4148fd7efb3667e58828e4d2b864f86201b85ff85d8203ddb8583056301006072a8648ce3d020106052b8104000a034200042a86469754777b30bc63304ac057db2882b1a69a81ac57b4dae3490f0df367d7232e81be05d5520742191a5d5254b0be544255ad4148fd7efb3667e58828e4d2",
        "signature": "95d4d9234f2553782eeeea7b9d0e94e21c64ee08b680e53c18375eaf16374f6ab394cb6a91647e5e5a023627fb4efd5748c03c95ecdc17bfda13ebc2594bcd8b"
    }


@when('I send transaction with its signature')
def send(parameters):
    client.input = mock_input_yes
    result = send_tx(node=TEST_NODE, port=TEST_PORT,
                     tx_hex=parameters["tx"],
                     signatures_hex=[parameters["signature"]])
    parameters["result"] = result


@then('I get acceptance')
def verify_result(parameters):
    assert parameters["result"]
