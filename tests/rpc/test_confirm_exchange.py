from pytest_bdd import scenario, given, when, then, parsers

from chasm.consensus.primitives.transaction import ConfirmationTransaction
from chasm.rpc import client
from chasm.rpc.client import get_transaction, do_confirm, do_offer_match, fetch_matches
from . import init_address, sleep_for_block, mock_acceptance


@scenario('test_confirm_exchange.feature', 'Exchange confirmation')
def test_confirm_exchange():
    pass


@given(
    parsers.parse('{maker} has {xpc1:d} bdzys in {utxos1:d} UTXO and {taker} has {xpc2:d} bdzys in {utxos2:d} UTXO'))
def parameters(chasm_server, alice_account, bob_account, maker, xpc1, utxos1, taker, xpc2, utxos2):
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
        "match": "",
        "confirmation": ""
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
    parameters["offer"] = offer.hex()
    assert get_transaction(node=node, port=test_port,
                           transaction=parameters["offer"]) is not None


@when(parsers.parse(
    '{taker} accepts the offer'))
def accept_offer(parameters, node, test_port, btc_addr, datadir, taker):
    client.input = mock_acceptance
    parameters[taker]["receive"] = btc_addr.hex()
    result, match = do_offer_match(node=node, port=test_port,
                                   sender=parameters[taker]["address"],
                                   offer_hash=parameters["offer"],
                                   receive_addr=btc_addr.hex(), tx_fee=1,
                                   conf_fee=2, deposit=12,
                                   datadir=datadir,
                                   signing_key=parameters[taker]["key"])
    assert result
    parameters["match"] = match.hash().hex()
    sleep_for_block()


@when('Carol confirms the exchange')
def confirm(parameters, carol_account, node, test_port, datadir, proof):
    client.input = mock_acceptance
    key, addr = carol_account
    result, tx = do_confirm(node=node, port=test_port, address=addr,
                            exchange=parameters['offer'], datadir=datadir,
                            proof_in=proof.hex(), proof_out=proof.hex(),
                            signing_key=key)

    assert result
    parameters['confirmation'] = tx.hash().hex()
    sleep_for_block()


@then(parsers.parse('There is {count:d} offer matched by {taker}'))
def check_existing_matches(parameters, node, test_port, count, taker):
    matches = fetch_matches(host=node, port=test_port,
                            match_addr=parameters[taker]["receive"])

    assert len(matches) == count


@then(parsers.parse('{Maker} has {count:d} accepted offer'))
def check_exisitng_accepted_offers(parameters, node, test_port, count, maker):
    matches = fetch_matches(host=node, port=test_port,
                            offer_addr=parameters[maker]["receive"])

    assert len(matches) == count


@then('Confirmation exists')
def check_existence(parameters, node, test_port):
    tx = get_transaction(node=node, port=test_port,
                         transaction=parameters["confirmation"])
    assert tx is not None
    assert isinstance(tx, ConfirmationTransaction)
