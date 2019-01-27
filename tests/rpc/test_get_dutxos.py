# pylint: disable=missing-docstring
import pytest
from pytest_bdd import scenario, given, when, then, parsers

from chasm.rpc.client import get_dutxos
from . import init_address, sleep_for_block

pytest.skip("Problem with timeouts and blocks creation", allow_module_level=True)


@scenario('test_get_dutxos.feature', 'Get DUTXOs of non-existing address')
def test_get_non_existing_utxos():
    pass


@scenario('test_get_dutxos.feature', 'Get DUTXOs of existing address')
def test_get_existing_utxos():
    pass


@given(parsers.parse('New address'))
def parameters(alice_account):
    _, address = alice_account
    return {
        "address": address
    }


@when('I get DUTXOs')
def get_utxos_from_server(parameters, node, test_port):
    dutxos = get_dutxos(address=parameters["address"],
                        port=test_port, node=node)
    parameters["dutxos"] = dutxos


@when('I sum DUTXOs')
def get_balance(parameters):
    balance = sum(dutxo["value"] for dutxo in parameters["dutxos"])
    parameters["balance"] = balance


@then(parsers.parse("Owner has {balance:d} bdzys in {dutxos:d} DUTXOs"))
def check_balance(parameters, balance, dutxos):
    assert parameters["balance"] == balance
    assert len(parameters["dutxos"]) == dutxos


@when(parsers.parse('Initialized address has {balance:d} bdzys in {dutxos:d} DUTXOs'))
def initialize(parameters, balance, dutxos):
    init_address(address=parameters["address"],
                 dutxos_sum=balance, dutxos=dutxos)
    sleep_for_block()
