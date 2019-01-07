import queue
import shutil
from queue import Empty

import pytest
from pytest import fixture

from chasm import consensus
from chasm.consensus import GENESIS_BLOCK, Block
from chasm.consensus.primitives.transaction import Transaction, MintingTransaction
from chasm.consensus.primitives.tx_input import TxInput
from chasm.consensus.primitives.tx_output import TransferOutput
from chasm.state.state import State

TEST_DB_PATH = '/tmp/xpeer'


@fixture
def empty_state():
    state = State(TEST_DB_PATH)
    yield state
    state.close()
    shutil.rmtree(TEST_DB_PATH)


@fixture
def transactions(alice):
    tx_hash = consensus.HASH_FUNC(b'beef').digest()
    return [Transaction([TxInput(tx_hash, i)], [TransferOutput(i, alice.pub)]) for i in range(5)]


@fixture
def transaction(transactions):
    return transactions[0]


@fixture
def empty_block(empty_state, alice):
    previous = empty_state.get_block_by_no(0)

    block = Block(previous.hash(), 0)

    block.add_transaction(MintingTransaction([TransferOutput(100, alice.pub)]))
    block.update_merkle_root()

    return block


def test_saves_pending_tx(empty_state, transaction):
    empty_state.add_pending_tx(transaction)
    assert empty_state.pop_pending_tx() == transaction


def test_pending_txs_fifo(empty_state, transactions):
    for tx in transactions:
        empty_state.add_pending_tx(tx)

    for tx in transactions:
        assert tx == empty_state.pop_pending_tx()


def test_throws_when_no_pending_txs(empty_state):
    with pytest.raises(Empty):
        empty_state.pop_pending_tx()


def test_respects_priority_of_pending_txs(empty_state, transactions):
    for i in range(len(transactions)):
        empty_state.add_pending_tx(transactions[i], priority=i)

    for tx in reversed(transactions):
        assert tx == empty_state.pop_pending_tx()


def test_removes_pending_txs_with_lowest_priority(empty_state, transactions, transaction):
    for i in range(len(transactions)):
        empty_state.add_pending_tx(transactions[i], priority=i)

    # overwrite already pending txs with ones of higher priority
    for i in range(10):
        empty_state.add_pending_tx(transaction, priority=100)

    for i in range(10):
        assert transaction == empty_state.pop_pending_tx()


def test_persists_pending_txs(empty_state, transactions):
    for tx, priority in zip(transactions, range(len(transactions), 0, -1)):
        empty_state.add_pending_tx(tx, priority)

    empty_state.close()
    restored_state = State(TEST_DB_PATH)

    for tx in transactions:
        assert tx == restored_state.pop_pending_tx()

    with pytest.raises(queue.Empty):
        restored_state.pop_pending_tx()

    restored_state.close()


def test_removes_pending_and_does_not_restore_them(empty_state, transactions):
    for tx, priority in zip(transactions, range(len(transactions), 0, -1)):
        empty_state.add_pending_tx(tx, priority)

    tx = empty_state.pop_pending_tx()
    transactions.remove(tx)

    empty_state.close()
    restored_state = State(TEST_DB_PATH)

    for tx in transactions:
        assert tx == restored_state.pop_pending_tx()

    with pytest.raises(queue.Empty):
        restored_state.pop_pending_tx()

    restored_state.close()


def test_empty_state_stores_initial_block_and_is_empty(empty_state):
    assert empty_state.get_block_by_no(0) == GENESIS_BLOCK

    with pytest.raises(KeyError):
        empty_state.get_block_by_no(1)

    assert empty_state.get_utxos() == {}
    assert empty_state.get_dutxos() == {}


def test_applies_an_empty_block_and_it_is_persisted(empty_state, empty_block):
    empty_state.apply_block(empty_block)

    assert empty_block == empty_state.get_block_by_no(1)
    assert empty_block == empty_state.get_block_by_hash(empty_block.hash())

    empty_state.close()
    restored_state = State(TEST_DB_PATH)

    assert empty_block == restored_state.get_block_by_no(1)
    assert empty_block == restored_state.get_block_by_hash(empty_block.hash())

    restored_state.close()


def test_applies_a_block_and_utxos_are_seen():
    pass
