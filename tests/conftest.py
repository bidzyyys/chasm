import json
import os
import shutil
from collections import namedtuple

from ecdsa import SigningKey
from merkletools import MerkleTools
from pytest import fixture

from chasm import consensus
from chasm.consensus.primitives.block import Block
from chasm.consensus.primitives.transaction import Transaction, SignedTransaction, MintingTransaction, OfferTransaction, \
    MatchTransaction, ConfirmationTransaction, UnlockingDepositTransaction
from chasm.consensus.primitives.tx_input import TxInput
from chasm.consensus.primitives.tx_output import TransferOutput, XpeerOutput, XpeerFeeOutput
from chasm.consensus.tokens import Tokens
from chasm.maintenance.config import Config, DEFAULT_CONFIG_FILE, \
    DEFAULT_CONFIG_DIR, DEFAULT_TEST_CONFIG
from chasm.rpc.client import do_offer, build_transfer_tx
from chasm.serialization.rlp_serializer import RLPSerializer

Entity = namedtuple("Entity", "priv pub")


def _account():
    key = SigningKey.generate(consensus.CURVE)
    return key, key.get_verifying_key().to_string().hex()


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
def test_config():
    test_config = Config([DEFAULT_TEST_CONFIG])
    return test_config


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


@fixture
def alice_account():
    return _account()


@fixture
def bob_account():
    return _account()


@fixture(scope='session')
def btc_addr():
    return b'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'


@fixture(scope='session')
def eth_addr():
    return b'aaaaaaaaaaaaaaaaaaaa'


@fixture(scope='session')
def xpc_addr(carol):
    return carol.pub


@fixture(scope='session')
def proof():
    return b'aaaa1234'


@fixture
def datadir(test_config):
    os.makedirs(test_config.get('datadir'), exist_ok=True)
    yield test_config.get('datadir')
    shutil.rmtree(test_config.get('datadir'))


@fixture(scope="session")
def test_port(test_config):
    return test_config.get('rpc_port')


@fixture(scope="session")
def node(config):
    return config.get('node')


@fixture
def invalid_tx_file(datadir):
    file = os.path.join(datadir, 'invalid.json')
    test = {
        "test": 1234
    }
    with open(file, 'w') as f:
        json.dump(test, f)

    yield file
    os.remove(file)


@fixture
def valid_tx_file(datadir, alice_account, bob_account):
    _, addr1 = alice_account
    _, addr2 = bob_account
    file = os.path.join(datadir, 'valid.json')
    test = {
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
                "receiver": addr2
            },
            {
                "type": "TransferOutput",
                "value": 989,
                "receiver": addr1
            }
        ]
    }
    with open(file, 'w') as f:
        json.dump(test, f)

    yield file
    os.remove(file)


@fixture
def exchange():
    return consensus.HASH_FUNC(b'dead').digest()


@fixture
def tx_input():
    return TxInput(tx_hash=consensus.HASH_FUNC(b'beef').digest(), output_no=2)


@fixture
def tx_transfer_output(alice):
    return TransferOutput(value=100, receiver=alice.pub)


@fixture
def tx_transfer_outputs(tx_transfer_output):
    return [tx_transfer_output] * 10


@fixture
def tx_xpeer_output(alice, bob, exchange):
    return XpeerOutput(value=100, receiver=alice.pub, sender=bob.pub, exchange=exchange)


@fixture
def tx_xpeer_fee_output(exchange):
    return XpeerFeeOutput(100)


@fixture
def transfer_transaction(tx_input, tx_transfer_output):
    return Transaction(inputs=[tx_input], outputs=[tx_transfer_output, tx_transfer_output])


@fixture
def signed_simple_transaction(alice, transfer_transaction):
    (priv_key, _pub) = alice
    return SignedTransaction.build_signed(transfer_transaction, [priv_key])


@fixture
def minting_transaction(tx_transfer_outputs):
    return MintingTransaction(tx_transfer_outputs, height=100)


@fixture
def xpeer_offer_transaction(tx_input, tx_transfer_outputs, alice):
    return OfferTransaction([tx_input], tx_transfer_outputs, Tokens.BITCOIN.value, Tokens.ETHEREUM.value, 10, 100,
                            alice.pub, 0, 1, 1000)


@fixture
def xpeer_match_transaction(xpeer_offer_transaction, tx_input, tx_transfer_outputs, bob):
    offer_hash = xpeer_offer_transaction.hash()
    return MatchTransaction([tx_input], tx_transfer_outputs, offer_hash, address_in=bob.pub)


@fixture
def xpeer_confirmation_transaction(xpeer_offer_transaction, tx_input, tx_transfer_outputs):
    offer_hash = xpeer_offer_transaction.hash()
    return ConfirmationTransaction([tx_input], tx_transfer_outputs, offer_hash, b'some proof', b'another proof')


@fixture
def xpeer_deposit_unlocking_transaction(xpeer_offer_transaction, tx_input, tx_transfer_outputs):
    offer_hash = xpeer_offer_transaction.hash()
    return UnlockingDepositTransaction([tx_input], tx_transfer_outputs, offer_hash, 0, b'some proof')


@fixture
def block(transfer_transaction, xpeer_offer_transaction, xpeer_deposit_unlocking_transaction, xpeer_match_transaction,
          xpeer_confirmation_transaction):
    transactions = [transfer_transaction, xpeer_offer_transaction, xpeer_deposit_unlocking_transaction,
                    xpeer_match_transaction, xpeer_confirmation_transaction]

    merkle_tree = MerkleTools(hash_type=consensus.HASH_FUNC_NAME)
    merkle_tree.add_leaf(values=[tx.hash().hex() for tx in transactions])
    merkle_tree.make_tree()
    merkle_root = bytes.fromhex(merkle_tree.get_merkle_root())

    return Block(b'', merkle_root=merkle_root, difficulty=0, transactions=transactions)


@fixture(scope="session")
def rlp_serializer():
    return RLPSerializer()


@fixture
def publish_offer(test_port, node, datadir):
    def _publish_offer(sender, signing_key, receive_addr,
                       token="btc", amount=1,
                       expected="xpc", price=1000,
                       deposit=12, confirmation_fee=2, tx_fee=1,
                       timeout="2020-02-01::00:00:00"):
        published, offer = do_offer(node=node, port=test_port,
                                    sender=sender,
                                    signing_key=signing_key,
                                    receive_addr=receive_addr,
                                    token=token, amount=amount,
                                    expected=expected, price=price,
                                    conf_fee=confirmation_fee,
                                    deposit=deposit, tx_fee=tx_fee,
                                    timeout_str=timeout,
                                    datadir=datadir)

        assert published
        return offer.hash()

    return _publish_offer


@fixture
def build_tx(test_port, node, datadir):
    def _build_tx(sender, receiver, amount=10, tx_fee=1):
        return build_transfer_tx(node=node, port=test_port,
                                 amount=amount, tx_fee=tx_fee,
                                 owner=sender, receiver=receiver)

    return _build_tx
