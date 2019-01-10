# pylint: disable=missing-docstring

from pytest_bdd import scenario, given, when, then, parsers

from chasm.consensus.primitives.transaction import OfferTransaction
from chasm.rpc import client
from chasm.rpc.client import do_offer, count_balance, \
    get_active_offers, get_transaction
from . import TEST_DATADIR, SAMPLE_PASSWORD, get_test_account, \
    TEST_NODE, TEST_PORT, get_private_key, mock_input_yes, \
    rlp_serializer, remove_dir, skip_test

pytestmark = skip_test()


@scenario('test_create_offer.feature', 'Alice creates exchange offer')
def test_create_offer():
    pass


@given(parsers.parse('Alice has {xpc:d} bdzys in {utxos:d} UTXO'))
def parameters(xpc, utxos):
    account_dict = get_test_account(balance=xpc, utxos=utxos)
    return account_dict


@when(parsers.parse(
    'Alice creates exchange offer: {amount:d} {token} for {price:d} {expected} until {timeout} confirmation fee {conf_fee:d} xpc transaction fee {tx_fee:d} xpc deposit {deposit:d} xpc with payment on her used address'))
def create_offer(parameters, amount, token, price, expected, timeout, conf_fee, tx_fee, deposit):
    client.input = mock_input_yes
    result, offer = do_offer(node=TEST_NODE, port=TEST_PORT,
                             sender=parameters["address"],
                             token=token, amount=amount,
                             expected=expected, price=price,
                             receive_addr=parameters["address"],
                             conf_fee=conf_fee, deposit=deposit,
                             timeout_str=timeout, tx_fee=tx_fee,
                             datadir=TEST_DATADIR,
                             signing_key=get_private_key(
                                 address=parameters["address"],
                                 datadir=TEST_DATADIR,
                                 password=SAMPLE_PASSWORD
                             ))
    parameters["offer"] = rlp_serializer.encode(offer).hex()


@then(parsers.parse('Alice has {balance:d} bdzys'))
def check_balance(parameters, balance):
    assert balance == count_balance(parameters["address"],
                                    node=TEST_NODE,
                                    port=TEST_PORT)


@then(parsers.parse('There is {count:d} active offer with token: {token} and expected: {expected}'))
def check_active_offers(count, token, expected):
    active_offers = get_active_offers(token=token, expected=expected,
                                      node=TEST_NODE, port=TEST_PORT)
    assert len(active_offers) == count


@then('Offer exists')
def check_existence(parameters):
    offer = get_transaction(node=TEST_NODE, port=TEST_PORT,
                            transaction=parameters["offer"])
    assert isinstance(offer, OfferTransaction)


@then('Cleanup is done')
def cleanup():
    remove_dir(TEST_DATADIR)
