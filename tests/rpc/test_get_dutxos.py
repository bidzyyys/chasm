# pylint: disable=missing-docstring
import pytest
from pytest_bdd import scenario, given, when, then, parsers

from chasm.rpc.client import get_dutxos
from . import check_server, TEST_NODE, TEST_PORT, init_address

pytestmark = pytest.mark.skipif(condition=check_server() is False,
                                reason="requires server running on {}:{}"
                                .format(TEST_NODE, TEST_PORT))


@scenario('test_get_dutxos.feature', 'Get DUTXOs of non-existing address')
def test_get_non_existing_utxos():
    pass


@scenario('test_get_dutxos.feature', 'Get DUTXOs of existing address')
def test_get_existing_utxos():
    pass


@given(parsers.parse('Address: {address}'))
def parameters(address):
    return {
        "address": address
    }


@when(parsers.parse('I get DUTXOs'))
def get_utxos_from_server(parameters):
    dutxos = get_dutxos(address=parameters["address"],
                        port=TEST_PORT, node=TEST_NODE)
    parameters["dutxos"] = dutxos


@when(parsers.parse('I sum DUTXOs'))
def get_balance(parameters):
    balance = sum(dutxo["value"] for dutxo in parameters["dutxos"])
    parameters["balance"] = balance


@then(parsers.parse("Address has {balance:d} bdzys in {dutxos:d} DUTXOs"))
def check_balance(parameters, balance, dutxos):
    assert balance == parameters["balance"]
    assert dutxos == len(parameters["dutxos"])


@when(parsers.parse('Initialized address has {balance:d} bdzys in {utxos:d} UTXOs'))
def initialize(parameters, balance, utxos):
    init_address(address=parameters["address"],
                 balance=balance, utxos=utxos)