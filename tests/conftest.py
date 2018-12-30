from collections import namedtuple

from ecdsa import SigningKey
from pytest import fixture

from chasm import consensus

Entity = namedtuple("Entity", "priv pub")


def __entity__():
    key = SigningKey.generate(consensus.CURVE)
    return Entity(key.to_string(), key.get_verifying_key().to_string())


@fixture(scope="session")
def alice():
    return __entity__()


@fixture(scope="session")
def bob():
    return __entity__()


@fixture(scope="session")
def carol():
    return __entity__()
