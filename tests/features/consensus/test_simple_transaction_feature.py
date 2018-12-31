# pylint: disable=missing-docstring, redefined-outer-name
from pytest import raises
from pytest_bdd import scenario, given, when, then, parsers


def verify_tx(all_funds, sender):
    if all_funds[sender]['after'] < 0:
        for owner in all_funds:
            all_funds[owner]['after'] = all_funds[owner]['before']
        raise ValueError("Invalid transaction")


@scenario('simple_transaction.feature', 'Valid simple transaction')
def test_valid_simple_transaction():
    pass


@scenario('simple_transaction.feature', 'Invalid simple transaction')
def test_invalid_simple_transaction():
    pass


@given(parsers.parse('{owner1} has {funds1:g} xpc and {owner2} has {funds2:g} xpc'))
def all_funds(owner1, funds1, owner2, funds2):
    return {
        owner1: {
            'before': funds1,
            'after': funds1,
        },
        owner2: {
            'before': funds2,
            'after': funds2
        }
    }


@when(parsers.parse('{sender} transfers {amount:g} xpc to {receiver} and pays {fee:g} xpc tx_fee'))
def transfer(all_funds, sender, amount, receiver, fee):
    all_funds[sender]['after'] -= fee
    all_funds[sender]['after'] -= amount
    all_funds[receiver]['after'] += amount


@then(parsers.parse('{sender} gets an error'))
def invalid_tx(all_funds, sender):
    with raises(ValueError):
        verify_tx(all_funds, sender)


@then(parsers.parse('{sender} gets an acceptance'))
def valid_tx(all_funds, sender):
    verify_tx(all_funds, sender)


@then(parsers.parse('Now {owner1} has {funds1:g} xpc and {owner2} has {funds2:g} xpc'))
def should_have_funds(all_funds, owner1, funds1, owner2, funds2):
    assert all_funds[owner1]['after'] == funds1
    assert all_funds[owner2]['after'] == funds2
