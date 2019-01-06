import shutil
from queue import Empty

import pytest
from pytest import fixture

from chasm import consensus
from chasm.consensus.primitives.transaction import Transaction
from chasm.consensus.primitives.tx_input import TxInput
from chasm.consensus.primitives.tx_output import TransferOutput
from chasm.state.state import State

TEST_DB_PATH = '/tmp/xpeer'


@fixture
def state():
    state = State(TEST_DB_PATH)
    yield state
    state.db.db.close()
    shutil.rmtree(TEST_DB_PATH)


@fixture
def transactions(alice):
    tx_hash = consensus.HASH_FUNC(b'beef').digest()
    return [Transaction([TxInput(tx_hash, i)], [TransferOutput(i, alice.pub)]) for i in range(5)]


@fixture
def transaction(transactions):
    return transactions[0]


def test_saves_pending_tx(state, transaction):
    state.add_pending_tx(transaction)
    assert state.pop_pending_tx() == transaction


def test_pending_txs_fifo(state, transactions):
    for tx in transactions:
        state.add_pending_tx(tx)

    for tx in transactions:
        assert tx == state.pop_pending_tx()


def test_throws_when_no_pending_txs(state):
    with pytest.raises(Empty):
        state.pop_pending_tx()


def test_respects_priority_of_pending_txs(state, transactions):
    for i in range(len(transactions)):
        state.add_pending_tx(transactions[i], priority=i)

    for tx in reversed(transactions):
        assert tx == state.pop_pending_tx()


def test_removes_pending_txs_with_lowest_priority(state, transactions, transaction):
    for i in range(len(transactions)):
        state.add_pending_tx(transactions[i], priority=i)

    # overwrite already pending txs with ones of higher priority
    for i in range(10):
        state.add_pending_tx(transaction, priority=100)

    for i in range(10):
        assert transaction == state.pop_pending_tx()


def test_persists_pending_txs(state, transactions):
    for tx in transactions:
        state.add_pending_tx(tx)

    state.db.db.close()
    restored_state = State(TEST_DB_PATH)

    # it is done in this way as we will not persist FIFO order of pending txs after shutdown
    should_continue = True
    while should_continue:
        try:
            popped = restored_state.pop_pending_tx()
            assert popped in transactions
            transactions.remove(popped)
        except Empty:
            should_continue = False

    assert not transactions

# def test_removes_pending_and_does_not_restore_them(state, transactions):
