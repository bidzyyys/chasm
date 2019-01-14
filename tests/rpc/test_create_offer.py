# pylint: disable=missing-docstring

from pytest_bdd import scenario, given, when, then, parsers

from chasm.consensus.primitives.transaction import OfferTransaction
from chasm.rpc import client
from chasm.rpc.client import count_balance, \
    get_active_offers, get_transaction
from . import skip_test, mock_acceptance, init_address, \
    sleep_for_block

# pytestmark = skip_test()


@scenario('test_create_offer.feature', 'Alice creates exchange offer')
def test_create_offer():
    pass


@given(parsers.parse('Alice has {xpc:d} bdzys in {utxos:d} UTXO'))
def parameters(chasm_server, alice_account, xpc, utxos):
    _, address = alice_account
    init_address(address=address, balance=xpc, utxos=utxos)
    return {
        "address": address,
        "offer": ""
    }


@when(parsers.parse(
    'Alice creates exchange offer: {amount:d} {token} for {price:d} {expected} until {timeout} confirmation fee {conf_fee:d} xpc transaction fee {tx_fee:d} xpc deposit {deposit:d} xpc with payment on her used address'))
def create_offer(parameters, alice_account, publish_offer, amount, token, price, expected,
                 timeout, conf_fee, tx_fee, deposit):
    sleep_for_block()
    signing_key, address = alice_account
    client.input = mock_acceptance
    offer = publish_offer(address, signing_key, address,
                          token, amount, expected, price,
                          deposit, conf_fee, tx_fee,
                          timeout)
    sleep_for_block()
    parameters["offer"] = offer.hex()


@then(parsers.parse('Alice has {balance:d} bdzys'))
def check_balance(parameters, balance, node, test_port):
    assert count_balance(parameters["address"],
                         node=node, port=test_port) == balance


@then(parsers.parse(
    'There is {count:d} active offer with token: {token} and expected: {expected}'))
def check_active_offers(count, token, expected, node, test_port):
    active_offers = get_active_offers(token=token, expected=expected,
                                      node=node, port=test_port)
    assert len(active_offers) == count


@then('Offer exists')
def check_existence(parameters, node, test_port):
    offer = get_transaction(node=node, port=test_port,
                            transaction=parameters["offer"])
    assert isinstance(offer, OfferTransaction)
