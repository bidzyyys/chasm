# pylint: disable=missing-docstring, redefined-outer-name
from os.path import isfile, isdir, join

from ecdsa import VerifyingKey
from pytest_bdd import scenario, given, when, then, parsers

from chasm.rpc import KEYSTORE
from chasm.rpc.client import create_account, get_addresses, \
    get_priv_key, get_account_data


@scenario('test_generate_key.feature', 'Key generation')
def test_generate_key():
    pass


@given(parsers.parse('Password: {pwd}'))
def parameters(datadir, pwd):
    return {
        "datadir": datadir,
        "pwd": pwd
    }


@when('Keystore does not exist')
def check_non_existance(parameters):
    assert isdir(join(parameters["datadir"],
                      KEYSTORE)) is False


@when('Alice creates new account')
def generate(parameters):
    _, keyfile = create_account(datadir=parameters["datadir"],
                                pwd=parameters["pwd"])

    assert isfile(keyfile)


@then('Keystore exists')
def check_existence(parameters):
    assert isdir(parameters["datadir"])


@then('Keys are valid')
def validate_keys(parameters):
    addresses = get_addresses(parameters["datadir"])
    assert isfile(addresses[0][1])
    account = get_account_data(datadir=parameters["datadir"],
                               pub_key_hex=addresses[0][0])
    priv_key = get_priv_key(account=account,
                            pwd=parameters["pwd"])

    pub_key = VerifyingKey.from_der(bytes.fromhex(addresses[0][0]))
    signature = priv_key.sign(b"message")
    assert pub_key.verify(signature, b"message")
