# pylint: disable=missing-docstring, redefined-outer-name

from os.path import isfile, isdir, join

from pytest_bdd import scenario, given, when, then, parsers

from chasm.rpc import KEYSTORE
from chasm.rpc.client import create_account, get_addresses
from . import remove_dir, create_dir_structure


@scenario('test_display_keys.feature', 'Display keys')
def test_display_keys():
    pass


@given(parsers.parse('Datadir: {datadir}, password: {pwd}'))
def parameters(datadir, pwd):
    return {
        "datadir": datadir,
        "pwd": pwd
    }


@when('Datadir exists with no keystore')
def check_existance(parameters):
    keystore = join(parameters["datadir"], KEYSTORE)
    if isdir(keystore):
        remove_dir(keystore)

    create_dir_structure(parameters["datadir"])
    parameters["keystore"] = keystore

    assert isdir(parameters["datadir"])
    assert isdir(keystore) is False


@when(parsers.parse('Alice creates {accounts:d} new accounts'))
def generate(parameters, accounts):
    for _ in range(accounts):
        _, keyfile = create_account(datadir=parameters["datadir"],
                                    pwd=parameters["pwd"])
        assert isfile(keyfile)


@then('Cleanup is done')
def cleanup(parameters):
    remove_dir(parameters["datadir"])
    assert isdir(parameters["datadir"]) is False


@then('Keystore exists')
def check_existence(parameters):
    assert isdir(parameters["keystore"])


@then(parsers.parse('{accounts:d} accounts are created'))
def ckeck_keys(parameters, accounts):
    addresses = get_addresses(parameters["datadir"])
    assert len(addresses) == accounts
