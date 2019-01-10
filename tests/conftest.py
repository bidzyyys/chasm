import os
from collections import namedtuple

from ecdsa import SigningKey
from pytest import fixture

from chasm import consensus
from chasm.maintenance.config import Config, DEFAULT_CONFIG_FILE, DEFAULT_CONFIG_DIR

Entity = namedtuple("Entity", "priv pub")


def _entity():
    key = SigningKey.generate(consensus.CURVE)
    return Entity(key.to_string(), key.get_verifying_key().to_string())


@fixture(scope="session")
def config(miner):
    config_files = [DEFAULT_CONFIG_FILE, os.path.join(DEFAULT_CONFIG_DIR, 'dev.ini')]
    config = Config(config_files)

    config.__setattr__('miner', lambda: miner.pub.hex())

    return config


@fixture(scope="session")
def miner():
    return _entity()


@fixture(scope="session")
def alice():
    return _entity()


@fixture(scope="session")
def bob():
    return _entity()


@fixture(scope="session")
def carol():
    return _entity()
