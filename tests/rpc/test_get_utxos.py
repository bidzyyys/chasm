# pylint: disable=missing-docstring
from pytest_bdd import scenario, given, when, then, parsers

from chasm.rpc.client import get_utxos, count_balance
from . import init_address, sleep_for_block


@scenario('test_get_utxos.feature', 'Get UTXOs of non-existing address')
def test_get_non_existing_utxos(node, test_port):
    pass


@scenario('test_get_utxos.feature', 'Get UTXOs of existing address')
def test_get_existing_utxos(node, test_port):
    pass


@given(parsers.parse('New address'))
def parameters(chasm_server, alice_account):
    _, address = alice_account
    return {
        "address": address
    }


@when('I get UTXOs')
def get_utxos_from_server(parameters, node, test_port):
    utxos = get_utxos(address=parameters["address"],
                      port=test_port, node=node)
    parameters["utxos"] = utxos


@when('I count balance of the account')
def get_balance(parameters, node, test_port):
    balance = count_balance(address=parameters["address"],
                            port=test_port, node=node)
    parameters["balance"] = balance


@then("UTXOs sum to balance")
def verify_balance(parameters):
    balance = sum(utxo["value"] for utxo in parameters["utxos"])
    assert parameters["balance"] == balance


@then(parsers.parse("Owner has {balance:d} bdzys in {utxos:d} UTXOs"))
def check_balance(parameters, balance, utxos):
    assert parameters["balance"] == balance
    assert len(parameters["utxos"]) == utxos


@when(parsers.parse('Initialized address has {balance:d} bdzys in {utxos:d} UTXOs'))
def initialize(parameters, balance, utxos):
    init_address(address=parameters["address"],
                 balance=balance, utxos=utxos)
    sleep_for_block()
