# pylint: disable=missing-docstring

from os.path import isdir

from pytest_bdd import scenario, given, when, then, parsers

from chasm.consensus.primitives.transaction import Transaction
from chasm.rpc import client
from chasm.rpc.client import do_simple_transfer, count_balance, \
    get_transaction
from . import SAMPLE_ADDR, TEST_PORT, TEST_NODE, \
    SAMPLE_PASSWORD, get_private_key, remove_dir, \
    mock_input_yes, TEST_DATADIR, skip_test, get_test_account

pytestmark = skip_test()


@scenario('test_simple_transfer.feature',
          'Alice sends to Bob some money')
def test_simple_transfer():
    pass


@given(parsers.parse('Alice has {xpc:d} bdzys in {utxos:d} UTXO'))
def parameters(xpc, utxos):
    account_dict = get_test_account(balance=xpc, utxos=utxos)
    return account_dict


@when(parsers.parse('Alice sends {xpc} bdzys to Bob with {tx_fee} bdzys transaction fee'))
def send(parameters, xpc, tx_fee):
    client.input = mock_input_yes
    result, tx = do_simple_transfer(node=TEST_NODE, port=TEST_PORT,
                                    amount=xpc, receiver=SAMPLE_ADDR,
                                    sender=parameters["address"], tx_fee=tx_fee,
                                    datadir=TEST_DATADIR,
                                    signing_key=get_private_key(
                                        address=parameters["address"],
                                        datadir=TEST_DATADIR,
                                        password=SAMPLE_PASSWORD
                                    ))
    parameters["result"] = result
    parameters["tx"] = tx.hash()


@then(parsers.parse('Alice has {alice_funds:d} bdzys and Bob has {bob_funds} bdzys'))
def verify_tx(parameters, alice_funds, bob_funds):
    assert parameters["result"]
    assert alice_funds == count_balance(parameters["address"], node=TEST_NODE, port=TEST_PORT)
    assert bob_funds == count_balance(SAMPLE_ADDR, node=TEST_NODE, port=TEST_PORT)


@then('Cleanup is done')
def cleanup(parameters):
    remove_dir(TEST_DATADIR)
    assert isdir(TEST_DATADIR) is False


@then('Transaction exists')
def check_existence(parameters):
    tx = get_transaction(node=TEST_NODE, port=TEST_PORT,
                         transaction=parameters["tx"])

    assert isinstance(tx, Transaction)
