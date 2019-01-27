# pylint: disable=missing-docstring
from pytest_bdd import scenario, given, when, then, parsers

from chasm.consensus import Side
from chasm.consensus.primitives.transaction import UnlockingDepositTransaction
from chasm.rpc import client
from chasm.rpc.client import get_transaction, do_unlock_deposit, do_offer_match
from . import init_address, mock_acceptance, sleep_for_block


@scenario('test_unlock_deposit.feature', 'Alice unlocks deposit')
def test_unlock_deposit():
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


@when(parsers.parse('{maker} creates UnlockDeposit transaction, deposit {deposit:d}, transaction fee {tx_fee:d}'))
def unlock(parameters, node, test_port, maker, datadir, deposit, tx_fee):
    client.input = mock_acceptance
    result, tx = do_unlock_deposit(node=node, port=test_port,
                                   sender=parameters[maker]["address"],
                                   offer_hash=parameters["offer"],
                                   deposit=deposit, tx_fee=tx_fee,
                                   side=Side.OFFER_MAKER.value,
                                   proof=parameters["offer"],
                                   datadir=datadir,
                                   signing_key=parameters[maker]["key"])

    assert result
    parameters["unlock"] = tx.hash().hex()
    sleep_for_block()


@then('UnlockDeposit transaction exists')
def check_unlock(parameters, node, test_port):
    unlock = get_transaction(node=node, port=test_port,
                             transaction=parameters["unlock"])

    assert unlock is not None
    assert isinstance(unlock, UnlockingDepositTransaction)
