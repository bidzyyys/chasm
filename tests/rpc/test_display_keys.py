# pylint: disable=missing-docstring, redefined-outer-name

from os.path import isfile, isdir, join

from pytest_bdd import scenario, given, when, then, parsers

from chasm.rpc import KEYSTORE
from chasm.rpc.client import create_account, get_addresses


@scenario('test_display_keys.feature', 'Display keys')
def test_display_keys():
    pass


@given(parsers.parse('Password for all keys: {pwd}'))
def parameters(datadir, pwd):
    return {
        "datadir": datadir,
        "pwd": pwd,
    }


@when(parsers.parse('Alice creates {accounts:d} new accounts'))
def generate(parameters, accounts):
    for _ in range(accounts):
        _, keyfile = create_account(datadir=parameters["datadir"],
                                    pwd=parameters["pwd"])
        assert isfile(keyfile)


@then('Keystore exists')
def check_existence(parameters):
    assert isdir(join(parameters["datadir"],
                      KEYSTORE))


@then(parsers.parse('{accounts:d} accounts exist'))
def check_keys(parameters, accounts):
    addresses = get_addresses(parameters["datadir"])
    assert accounts == len(addresses)
