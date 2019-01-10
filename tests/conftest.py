import os
from collections import namedtuple

from ecdsa import SigningKey
from pytest import fixture

from chasm import consensus
from chasm.config import Config

Entity = namedtuple("Entity", "priv pub")


def __entity__():
    key = SigningKey.generate(consensus.CURVE)
    return Entity(key.to_string(), key.get_verifying_key().to_string())


@fixture(scope="session")
def config():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_dir = os.path.abspath(os.path.join(dir_path, "../config"))
    config_files = [os.path.join(config_dir, file) for file in ['config.ini', 'dev.ini']]

    return Config(config_files)


@fixture(scope="session")
def alice():
    return __entity__()


@fixture(scope="session")
def bob():
    return __entity__()


@fixture(scope="session")
def carol():
    return __entity__()
