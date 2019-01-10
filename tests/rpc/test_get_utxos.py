# pylint: disable=missing-docstring
from pytest_bdd import scenario, given, when, then, parsers

from chasm.rpc.client import get_utxos, count_balance
from . import skip_test, TEST_NODE, TEST_PORT, init_address

pytestmark = skip_test()


@scenario('test_get_utxos.feature', 'Get UTXOs of non-existing address')
def test_get_non_existing_utxos():
    pass


@scenario('test_get_utxos.feature', 'Get UTXOs of existing address')
def test_get_existing_utxos():
    pass


@given(parsers.parse('Address: {address}'))
def parameters(address):
    return {
        "address": address
    }


@when('I get UTXOs')
def get_utxos_from_server(parameters):
    utxos = get_utxos(address=parameters["address"],
                      port=TEST_PORT, node=TEST_NODE)
    print(utxos)
    parameters["utxos"] = utxos


@when('I count balance of the account')
def get_balance(parameters):
    balance = count_balance(address=parameters["address"],
                            port=TEST_PORT, node=TEST_NODE)
    parameters["balance"] = balance


@then("UTXOs sum to balance")
def verify_balance(parameters):
    balance = sum(utxo["value"] for utxo in parameters["utxos"])
    assert balance == parameters["balance"]


@then(parsers.parse("Address has {balance:d} bdzys in {utxos:d} UTXOs"))
def check_balance(parameters, balance, utxos):
    assert balance == parameters["balance"]
    assert utxos == len(parameters["utxos"])


@when(parsers.parse('Initialized address has {balance:d} bdzys in {utxos:d} UTXOs'))
def initialize(parameters, balance, utxos):
    init_address(address=parameters["address"],
                 balance=balance, utxos=utxos)
