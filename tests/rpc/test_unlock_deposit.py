# pylint: disable=missing-docstring
from pytest_bdd import scenario, given, when, then, parsers

from chasm.consensus.primitives.transaction import UnlockingDepositTransaction
from chasm.rpc import Side
from chasm.rpc.client import get_transaction, do_unlock_deposit, count_balance
from . import get_test_account, publish_test_offer, remove_dir, \
    TEST_NODE, TEST_PORT, TEST_DATADIR, get_private_key, skip_test

pytestmark = skip_test()


@scenario('test_unlock_deposit.feature', 'Alice unlocks deposit')
def test_unlock_deposit():
    pass


@given(parsers.parse('{owner} has {xpc:d} bdzys in {utxos:d} UTXO'))
def parameters(owner, xpc, utxos):
    return {
        owner: {
            "address": get_test_account(balance=xpc, utxos=utxos)["address"]
        },
        "offer": "",
        "unlock": ""
    }


@when(parsers.parse(
    '{sender} creates exchange offer: {amount:d} {token} for {price:d} {expected}, receive {receive_addr}, deposit: {deposit:d}, transaction fee: {tx_fee:d} confirmation fee: {conf_fee:d}'))
def create_offer(parameters, sender, amount, token, price, expected,
                 receive_addr, deposit, tx_fee, conf_fee):
    offer = publish_test_offer(sender=parameters[sender]["address"],
                               token=token, amount=amount,
                               expected=expected, price=price,
                               receive_addr=receive_addr,
                               deposit=deposit, tx_fee=tx_fee,
                               confirmation_fee=conf_fee)

    assert get_transaction(node=TEST_NODE, port=TEST_PORT, transaction=offer) is not None
    parameters["offer"] = offer


@when(parsers.parse('{sender} creates UnlockDeposit transaction, deposit {deposit:d}, transaction fee {tx_fee:d}'))
def unlock(parameters, sender, deposit, tx_fee):
    result, unlock = do_unlock_deposit(node=TEST_NODE, port=TEST_PORT,
                                       sender=parameters[sender]["address"],
                                       offer_hash=parameters["offer"],
                                       deposit=deposit, tx_fee=tx_fee,
                                       side=Side.OFFER_MAKER.value,
                                       proof=parameters["offer"],
                                       datadir=TEST_DATADIR,
                                       signing_key=get_private_key(
                                           address=parameters[sender]["address"]
                                       ))

    assert result
    parameters["unlock"] = unlock.hash()


@then('UnlockDeposit transaction exists')
def check_unlock(parameters):
    unlock = get_transaction(node=TEST_NODE, port=TEST_PORT,
                             transaction=parameters["unlock"])

    assert unlock is not None
    assert isinstance(unlock, UnlockingDepositTransaction)


@then(parsers.parse('{owner} has {amount:d} xpc'))
def check_funds(parameters, owner, amount):
    assert amount == count_balance(parameters[owner]["address"],
                                   node=TEST_NODE, port=TEST_PORT)


@then('Cleanup is done')
def cleanup():
    remove_dir(TEST_DATADIR)
