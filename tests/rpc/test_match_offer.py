# pylint: disable=missing-docstring

from pytest_bdd import scenario, given, when, then, parsers

from chasm.consensus.primitives.transaction import MatchTransaction
from chasm.rpc.client import get_transaction, do_offer_match, \
    count_balance, fetch_matches
from . import get_test_account, publish_test_offer, TEST_NODE, \
    TEST_PORT, TEST_DATADIR, get_private_key, skip_test, remove_dir

pytestmark = skip_test()


@scenario('test_match_offer.feature', 'Bob matches offer')
def test_match_offer():
    pass


@given(
    parsers.parse('{owner1} has {xpc1:d} bdzys in {utxos1:d} UTXO and {owner2} has {xpc2:d} bdzys in {utxos2:d} UTXO'))
def parameters(owner1, xpc1, utxos1, owner2, xpc2, utxos2):
    return {
        owner1: {
            "address": get_test_account(balance=xpc1, utxos=utxos1)["address"]
        },
        owner2: {
            "address": get_test_account(balance=xpc2, utxos=utxos2)["address"]
        },
        "offer": "",
        "match": ""
    }


@when(parsers.parse(
    '{sender} creates exchange offer: {amount:d} {token} for {price:d} {expected}, receive {receive_addr}'))
def create_offer(parameters, sender, amount, token, price, expected, receive_addr):
    offer = publish_test_offer(sender=parameters[sender]["address"],
                               token=token, amount=amount,
                               expected=expected, price=price,
                               receive_addr=receive_addr)

    parameters[sender]["receive"] = receive_addr
    assert get_transaction(node=TEST_NODE, port=TEST_PORT, transaction=offer) is not None
    parameters["offer"] = offer


@when(parsers.parse(
    '{sender} accepts it deposit: {deposit:d}, confirmation fee: {conf_fee:d}, transaction fee: {tx_fee:d}, receive {receive_addr}'))
def accept_offer(parameters, sender, deposit, conf_fee, tx_fee, receive_addr):
    parameters[sender]["receive"] = receive_addr
    result, match = do_offer_match(node=TEST_NODE, port=TEST_PORT,
                                   sender=parameters[sender]["address"],
                                   offer_hash=parameters["offer"],
                                   receive_addr=receive_addr, tx_fee=tx_fee,
                                   conf_fee=conf_fee, deposit=deposit,
                                   datadir=TEST_DATADIR,
                                   signing_key=get_private_key(
                                       address=parameters[sender]["address"]
                                   ))
    assert result
    parameters["match"] = match.hash()


@then('Offer match exists')
def check_existence(parameters):
    tx = get_transaction(node=TEST_NODE, port=TEST_PORT,
                         transaction=parameters["match"])
    assert tx is not None
    assert isinstance(tx, MatchTransaction)


@then(parsers.parse('{owner} has {amount:d} xpc'))
def check_funds(parameters, owner, amount):
    assert amount == count_balance(parameters[owner]["address"],
                                   node=TEST_NODE, port=TEST_PORT)


@then(parsers.parse('There is {count:d} accepted offer by {creator}'))
def check_exisitng_accepted_offers(parameters, count, creator):
    matches = fetch_matches(host=TEST_NODE, port=TEST_PORT,
                            offer_addr=parameters[creator]["receive"])

    assert len(matches) == count


@then(parsers.parse('There is {count:d} offer match by {creator}'))
def check_existing_matches(parameters, count, creator):
    matches = fetch_matches(host=TEST_NODE, port=TEST_PORT,
                            match_addr=parameters[creator]["receive"])

    assert len(matches) == count


@then('There is no accepted offer with fake address')
def assert_offers_non_existence():
    assert fetch_matches(host=TEST_NODE, port=TEST_PORT,
                         offer_addr="0000") is None


@then('There is no offer match with fake address')
def assert_matches_non_existence():
    assert fetch_matches(host=TEST_NODE, port=TEST_PORT,
                         match_addr="0000") is None


@then('Cleanup is done')
def cleanup():
    remove_dir(TEST_DATADIR)
