# pylint: disable=missing-docstring

from os.path import isdir

from pytest_bdd import scenario, given, when, then, parsers

from chasm.consensus.primitives.transaction import Transaction
from chasm.rpc import client
from chasm.rpc.client import do_simple_transfer, count_balance, \
    get_transaction
from . import mock_acceptance, skip_test, init_address

pytestmark = skip_test()


@scenario('test_simple_transfer.feature',
          'Alice sends to Bob some money')
def test_simple_transfer():
    pass


@given(parsers.parse('{owner1} has {xpc1:d} bdzys in {utxos1:d} UTXO and {owner2} has {xpc2} bdzys in {utxos2:d} UTXO'))
def parameters(alice_account, bob_account, owner1, owner2, xpc1, utxos1, xpc2, utxos2):
    key1, addr1 = alice_account
    init_address(address=addr1, balance=xpc1, utxos=utxos1)
    key2, addr2 = bob_account
    init_address(address=addr2, balance=xpc2, utxos=utxos2)
    return {
        owner1: {
            "address": addr1,
            "key": key1
        },
        owner2: {
            "address": addr2,
            "key": key2
        }
    }


@when(parsers.parse('{sender} sends {xpc:d} bdzys to {receiver} with {tx_fee:d} bdzys transaction fee'))
def send(parameters, node, test_port, datadir,
         sender, receiver, xpc, tx_fee):
    client.input = mock_acceptance
    result, tx = do_simple_transfer(node=node, port=test_port,
                                    amount=xpc, receiver=parameters[receiver]["address"],
                                    sender=parameters[sender]["address"], tx_fee=tx_fee,
                                    datadir=datadir,
                                    signing_key=parameters[sender]["key"])
    assert result
    parameters["tx"] = tx.hash()


@then(parsers.parse('{owner} has {funds:d} bdzys'))
def verify_tx(parameters, node, test_port, owner, funds):
    assert count_balance(parameters[owner]["address"],
                         node=node, port=test_port) == funds


@then('Transaction exists')
def check_existence(parameters, node, test_port):
    tx = get_transaction(node=node, port=test_port,
                         transaction=parameters["tx"])

    assert isinstance(tx, Transaction)
