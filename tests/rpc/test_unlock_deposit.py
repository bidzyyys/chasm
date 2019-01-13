# pylint: disable=missing-docstring
from pytest_bdd import scenario, given, when, then, parsers

from chasm.consensus import Side
from chasm.consensus.primitives.transaction import UnlockingDepositTransaction
from chasm.rpc import client
from chasm.rpc.client import get_transaction, do_unlock_deposit
from . import skip_test, init_address, mock_acceptance

pytestmark = skip_test()


@scenario('test_unlock_deposit.feature', 'Alice unlocks deposit')
def test_unlock_deposit():
    pass


@given(parsers.parse('{owner} has {xpc:d} bdzys in {utxos:d} UTXO'))
def parameters(alice_account, owner, xpc, utxos):
    key, address = alice_account
    init_address(address=address, balance=xpc, utxos=utxos)
    return {
        owner: {
            "address": address,
            "key": key
        },
        "offer": "",
        "unlock": ""
    }


@when(parsers.parse(
    '{maker} creates an exchange offer'))
def create_offer(parameters, node, test_port, publish_offer,
                 maker):
    client.input = mock_acceptance
    offer = publish_offer(parameters[maker]["address"],
                          parameters[maker]["key"],
                          parameters[maker]["address"])

    assert get_transaction(node=node, port=test_port, transaction=offer) is not None
    parameters["offer"] = offer


@when(parsers.parse('{maker} creates UnlockDeposit transaction, deposit {deposit:d}, transaction fee {tx_fee:d}'))
def unlock(parameters, node, test_port, maker, datadir, deposit, tx_fee):
    client.input = mock_acceptance
    result, unlock = do_unlock_deposit(node=node, port=test_port,
                                       sender=parameters[maker]["address"],
                                       offer_hash=parameters["offer"],
                                       deposit=deposit, tx_fee=tx_fee,
                                       side=Side.OFFER_MAKER.value,
                                       proof=parameters["offer"],
                                       datadir=datadir,
                                       signing_key=parameters[maker]["key"])

    assert result
    parameters["unlock"] = unlock.hash()


@then('UnlockDeposit transaction exists')
def check_unlock(parameters, node, test_port):
    unlock = get_transaction(node=node, port=test_port,
                             transaction=parameters["unlock"])

    assert unlock is not None
    assert isinstance(unlock, UnlockingDepositTransaction)
