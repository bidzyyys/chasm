# pylint: disable=missing-docstring, redefined-outer-name
from os import remove
from os.path import isfile

from pytest import raises
from pytest_bdd import scenario, given, when, then

from chasm.consensus.primitives.transaction import Transaction
from chasm.rpc.client import build_tx_from_json, save_json


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
def valid():
    tx = {
        "type": "Transaction",
        "inputs": [
            {
                "type": "TxInput",
                "tx_hash": "5465737473",
                "output_no": 69
            }
        ],
        "outputs": [
            {
                "type": "TransferOutput",
                "value": 10,
                "receiver": "3056301006072a8648ce3d020106052b8104000a034200042a86469754777b30bc63304ac057db2882b1a69a81ac57b4dae3490f0df367d7232e81be05d5520742191a5d5254b0be544255ad4148fd7efb3667e58828e4d2"
            },
            {
                "type": "TransferOutput",
                "value": 989,
                "receiver": "3056301006072a8648ce3d020106052b8104000a034200042a86469754777b30bc63304ac057db2882b1a69a81ac57b4dae3490f0df367d7232e81be05d5520742191a5d5254b0be544255ad4148fd7efb3667e58828e4d2"
            }
        ]
    }

    save_json(data=tx, filename="valid.json")
    return {
        "file": "valid.json"
    }


@given('Invalid file with json')
def invalid():
    test = {
        "test": 1234
    }
    save_json(data=test, filename="invalid.json")

    return "invalid.json"


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


@then('File is removed')
def remove_valid_file(valid):
    cleanup(valid["file"])
    assert True


@then('Invalid file is removed')
def remove_invalid_file(invalid):
    cleanup(invalid)


def cleanup(file):
    remove(file)
    assert isfile(file) is False
