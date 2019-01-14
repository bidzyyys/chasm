# pylint: disable=missing-docstring

from pytest_bdd import scenario, given, when, then, parsers

from chasm.consensus.primitives.transaction import MatchTransaction
from chasm.rpc import client
from chasm.rpc.client import get_transaction, do_offer_match, \
    count_balance, fetch_matches
from . import skip_test, init_address, mock_acceptance, \
    sleep_for_block

pytestmark = skip_test()


@scenario('test_match_offer.feature', 'Bob matches offer')
def test_match_offer():
    pass


@given(
    parsers.parse('{maker} has {xpc1:d} bdzys in {utxos1:d} UTXO and {taker} has {xpc2:d} bdzys in {utxos2:d} UTXO'))
def parameters(alice_account, bob_account, maker, xpc1, utxos1, taker, xpc2, utxos2):
    key1, addr1 = alice_account
    init_address(addr1, balance=xpc1, utxos=utxos1)
    key2, addr2 = bob_account
    init_address(addr2, balance=xpc2, utxos=utxos2)
    return {
        maker: {
            "address": addr1,
            "key": key1
        },
        taker: {
            "address": addr2,
            "key": key2
        },
        "offer": "",
        "match": ""
    }


@when(parsers.parse(
    '{maker} creates exchange offer: {amount:d} {token} for {price:d} {expected}'))
def create_offer(parameters, node, test_port, publish_offer,
                 maker, amount, token, price, expected):
    sleep_for_block()
    client.input = mock_acceptance
    offer = publish_offer(parameters[maker]["address"],
                          parameters[maker]["key"],
                          parameters[maker]["address"],
                          token, amount, expected, price)

    sleep_for_block()
    parameters[maker]["receive"] = parameters[maker]["address"]
    assert get_transaction(node=node, port=test_port, transaction=offer) \
           is not None
    parameters["offer"] = offer


@when(parsers.parse(
    '{taker} accepts it deposit: {deposit:d}, confirmation fee: {conf_fee:d}, transaction fee: {tx_fee:d}, receive {receive_addr}'))
def accept_offer(parameters, node, test_port, datadir,
                 taker, deposit, conf_fee, tx_fee, receive_addr):
    parameters[taker]["receive"] = receive_addr
    client.input = mock_acceptance
    result, match = do_offer_match(node=node, port=test_port,
                                   sender=parameters[taker]["address"],
                                   offer_hash=parameters["offer"],
                                   receive_addr=receive_addr, tx_fee=tx_fee,
                                   conf_fee=conf_fee, deposit=deposit,
                                   datadir=datadir,
                                   signing_key=parameters[taker]["key"])
    assert result
    parameters["match"] = match.hash()
    sleep_for_block()

@then('Offer match exists')
def check_existence(parameters, node, test_port):
    tx = get_transaction(node=node, port=test_port,
                         transaction=parameters["match"])
    assert tx is not None
    assert isinstance(tx, MatchTransaction)


@then(parsers.parse('{owner} has {amount:d} xpc'))
def check_funds(parameters, node, test_port, owner, amount):
    assert count_balance(parameters[owner]["address"],
                         node=node, port=test_port) == amount


@then(parsers.parse('There is {count:d} accepted offer by {creator}'))
def check_exisitng_accepted_offers(parameters, node, test_port, count, creator):
    matches = fetch_matches(host=node, port=test_port,
                            offer_addr=parameters[creator]["receive"])

    assert len(matches) == count


@then(parsers.parse('There is {count:d} offer match by {creator}'))
def check_existing_matches(parameters, node, test_port, count, creator):
    matches = fetch_matches(host=node, port=test_port,
                            match_addr=parameters[creator]["receive"])

    assert len(matches) == count


@then('There is no accepted offer with fake address')
def assert_offers_non_existence(node, test_port):
    assert fetch_matches(host=node, port=test_port,
                         offer_addr="0000") is None


@then('There is no offer match with fake address')
def assert_matches_non_existence(node, test_port):
    assert fetch_matches(host=node, port=test_port,
                         match_addr="0000") is None

