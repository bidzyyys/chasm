# pylint: disable=missing-docstring, redefined-outer-name

from pytest import raises
from pytest_bdd import scenario, given, when, then

from chasm.consensus.primitives.transaction import Transaction
from chasm.rpc.client import build_tx_from_json


@scenario('test_build_tx.feature', 'Build transaction from file')
def test_build_valid_tx():
    pass


@scenario('test_build_tx.feature',
          'Build transaction from file')
def test_build_valid_tx():
    pass


@scenario('test_build_tx.feature',
          'Failed to build transaction from invalid file')
def test_build_invalid_tx():
    pass


@given('File with transaction in json format')
def valid(valid_tx_file):
    return {
        "file": valid_tx_file
    }


@given('Invalid file with json')
def invalid(invalid_tx_file):
    return invalid_tx_file


@when('I build tx from file')
def build_tx(valid):
    tx = build_tx_from_json(valid["file"])
    valid["tx"] = tx


@then('I get transaction')
def verify_tx(valid):
    assert isinstance(valid["tx"], Transaction)
    assert len(valid["tx"].inputs) == 1
    assert len(valid["tx"].outputs) == 2


@then('I get RuntimeError while building transaction')
def failed_build(invalid):
    with raises(RuntimeError):
        build_tx_from_json(invalid)
