import queue
import shutil
from queue import Empty

import pytest
from pytest import fixture

from chasm import consensus
from chasm.consensus import GENESIS_BLOCK, Block
from chasm.consensus.primitives.transaction import Transaction, MintingTransaction, SignedTransaction, OfferTransaction, \
    MatchTransaction, ConfirmationTransaction, UnlockingDepositTransaction
from chasm.consensus.primitives.tx_input import TxInput
from chasm.consensus.primitives.tx_output import TransferOutput, XpeerFeeOutput
from chasm.consensus.tokens import Tokens
from chasm.maintenance.exceptions import TxOverwriteError
from chasm.state.state import State


class RestoredState:
    def __init__(self, prev_state, data_dir, pending_queue_size):
        self.prev_state = prev_state

        self.pending_size = pending_queue_size
        self.data_dir = data_dir

    def __enter__(self):
        self.prev_state.close()
        self.state = State(self.data_dir, self.pending_size)
        return self.state

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.state.close()


@fixture
def empty_state(config):
    data_dir = config.get('datadir')
    pending_size = config.get('xpeer_pending_txs')

    shutil.rmtree(data_dir, ignore_errors=True)

    state = State(data_dir, pending_size)
    yield state

    state.close()
    shutil.rmtree(data_dir)


@fixture
def restored_state(empty_state, config):
    data_dir = config.get('datadir')
    pending_size = config.get('xpeer_pending_txs')

    return RestoredState(empty_state, data_dir, pending_size)


@fixture
def pending_transactions(alice):
    tx_hash = consensus.HASH_FUNC(b'beef').digest()
    return [
        SignedTransaction(Transaction([TxInput(tx_hash, i)], [TransferOutput(i, alice.pub)]), [b'beef'])
        for i in range(5)
    ]


@fixture
def pending_transaction(pending_transactions):
    return pending_transactions[0]


@fixture
def minting_transaction(alice, bob):
    outputs = [TransferOutput(100, alice.pub), TransferOutput(100, bob.pub)]
    return MintingTransaction(outputs, height=100)


@fixture
def offer_transaction(alice, utxo):
    tx = OfferTransaction([TxInput(*utxo)], outputs=[XpeerFeeOutput(50), TransferOutput(10, alice.pub)],
                          token_in=Tokens.ETHEREUM.value, token_out=Tokens.BITCOIN.value, value_in=1, value_out=2,
                          address_out=alice.pub, confirmation_fee_index=0, deposit_index=1, timeout=2**32)

    return SignedTransaction.build_signed(tx, [alice.priv])


@fixture
def match_transaction(bob, offer_transaction, second_utxo):
    match = MatchTransaction(inputs=[TxInput(*second_utxo)], outputs=[XpeerFeeOutput(50), TransferOutput(10, bob.pub)],
                             exchange=offer_transaction.hash(), address_in=bob.pub, confirmation_fee_index=0,
                             deposit_index=1)

    return SignedTransaction.build_signed(match, [bob.priv])


@fixture
def confirmation_transaction(carol, offer_transaction, match_transaction, utxos_from_filled_state):
    tx_inputs = [TxInput(offer_transaction.hash(), 0), TxInput(match_transaction.hash(), 0),
                 TxInput(*(utxos_from_filled_state[2]))]

    tx = ConfirmationTransaction(inputs=tx_inputs, outputs=[TransferOutput(100, carol.pub)],
                                 exchange=offer_transaction.hash(), tx_in_proof=b'proof', tx_out_proof=b'other-proof')

    return SignedTransaction.build_signed(tx, [carol.priv])


@fixture
def unlocking_transactions(alice, bob, offer_transaction, match_transaction, utxos_from_filled_state):
    tx_inputs = [TxInput(offer_transaction.hash(), 0), TxInput(match_transaction.hash(), 0),
                 TxInput(*(utxos_from_filled_state[2]))]

    unlocking1 = UnlockingDepositTransaction(inputs=tx_inputs, outputs=[TransferOutput(100, alice.pub)],
                                             exchange=offer_transaction.hash(), proof_side=0, tx_proof=b'proof')

    unlocking2 = UnlockingDepositTransaction(inputs=tx_inputs, outputs=[TransferOutput(100, alice.pub)],
                                             exchange=offer_transaction.hash(), proof_side=1, tx_proof=b'proof')

    return (SignedTransaction.build_signed(unlocking1, [alice.priv]),
            SignedTransaction.build_signed(unlocking2, [bob.priv]))


@fixture
def block_with_minting_tx(empty_state, minting_transaction):
    previous = empty_state.get_block_by_no(0)

    block = Block(previous.hash(), 0)

    block.add_transaction(minting_transaction)
    block.update_merkle_root()

    return block


@fixture
def filled_state(empty_state, alice):
    output = TransferOutput(100, alice.pub)

    for i in range(100):
        block = next_empty_block(empty_state)
        block.add_transaction(MintingTransaction(outputs=[output], height=empty_state.current_height + 1))
        block.update_merkle_root()
        empty_state.apply_block(block)

    return empty_state


@fixture
def utxo(filled_state):
    return list(filled_state.get_utxos().keys())[0]


@fixture
def second_utxo(filled_state):
    return list(filled_state.get_utxos().keys())[1]


@fixture
def filled_state_with_matched_offer(filled_state, offer_transaction, match_transaction):
    next_block = next_empty_block(filled_state)
    next_block.add_transaction(offer_transaction)
    next_block.update_merkle_root()
    filled_state.apply_block(next_block)

    next_block = next_empty_block(filled_state)
    next_block.add_transaction(match_transaction)
    next_block.update_merkle_root()
    filled_state.apply_block(next_block)

    return filled_state


@fixture
def utxos_from_filled_state(filled_state):
    return list(filled_state.get_utxos().keys())


def next_empty_block(state):
    prev_hash = state.get_block_by_no(state.current_height).hash()
    return Block(prev_hash, 0)


def test_saves_pending_tx(empty_state, pending_transaction):
    empty_state.add_pending_tx(pending_transaction)
    assert empty_state.pop_pending_tx() == pending_transaction


def test_pending_txs_fifo(empty_state, pending_transactions):
    for tx in pending_transactions:
        empty_state.add_pending_tx(tx)

    for tx in pending_transactions:
        assert tx == empty_state.pop_pending_tx()


def test_throws_when_no_pending_txs(empty_state):
    with pytest.raises(Empty):
        empty_state.pop_pending_tx()


def test_respects_priority_of_pending_txs(empty_state, pending_transactions):
    for i in range(len(pending_transactions)):
        empty_state.add_pending_tx(pending_transactions[i], priority=i)

    for tx in reversed(pending_transactions):
        assert tx == empty_state.pop_pending_tx()


def test_removes_pending_txs_with_lowest_priority(empty_state, pending_transactions, pending_transaction):
    for i in range(len(pending_transactions)):
        empty_state.add_pending_tx(pending_transactions[i], priority=i)

    # overwrite already pending txs with ones of higher priority
    for i in range(10):
        empty_state.add_pending_tx(pending_transaction, priority=100)

    for i in range(10):
        assert pending_transaction == empty_state.pop_pending_tx()


def test_persists_pending_txs(empty_state, restored_state, pending_transactions):
    for tx, priority in zip(pending_transactions, range(len(pending_transactions), 0, -1)):
        empty_state.add_pending_tx(tx, priority)

    with restored_state as state:
        for tx in pending_transactions:
            assert tx == state.pop_pending_tx()

        with pytest.raises(queue.Empty):
            state.pop_pending_tx()


def test_removes_pending_and_does_not_restore_them(empty_state, restored_state, pending_transactions):
    for tx, priority in zip(pending_transactions, range(len(pending_transactions), 0, -1)):
        empty_state.add_pending_tx(tx, priority)

    tx = empty_state.pop_pending_tx()
    pending_transactions.remove(tx)

    with restored_state as state:
        for tx in pending_transactions:
            assert tx == state.pop_pending_tx()

        with pytest.raises(queue.Empty):
            state.pop_pending_tx()


def test_empty_state_stores_initial_block_and_is_empty(empty_state):
    assert empty_state.get_block_by_no(0) == GENESIS_BLOCK

    with pytest.raises(KeyError):
        empty_state.get_block_by_no(1)

    assert empty_state.get_utxos() == {}
    assert empty_state.get_dutxos() == {}


def test_applies_an_empty_block_and_it_is_persisted(empty_state, restored_state, block_with_minting_tx):
    empty_state.apply_block(block_with_minting_tx)

    assert block_with_minting_tx == empty_state.get_block_by_no(1)
    assert block_with_minting_tx == empty_state.get_block_by_hash(block_with_minting_tx.hash())

    with restored_state as state:
        assert block_with_minting_tx == state.get_block_by_no(1)
        assert block_with_minting_tx == state.get_block_by_hash(block_with_minting_tx.hash())


def test_applies_a_block_and_utxos_are_seen(empty_state, block_with_minting_tx, minting_transaction):
    empty_state.apply_block(block_with_minting_tx)

    assert minting_transaction.outputs.__len__() == empty_state.get_utxos().__len__()
    for i in range(minting_transaction.outputs.__len__()):
        assert empty_state.get_utxo(minting_transaction.hash(), i) == minting_transaction.outputs[i]


def test_persists_new_utxos(empty_state, restored_state, block_with_minting_tx, minting_transaction):
    empty_state.apply_block(block_with_minting_tx)

    with restored_state as state:
        assert minting_transaction.outputs.__len__() == state.get_utxos().__len__()
        for i in range(minting_transaction.outputs.__len__()):
            assert state.get_utxo(minting_transaction.hash(), i) == minting_transaction.outputs[i]


def test_can_use_an_already_existing_utxo(filled_state, alice, bob):
    an_utxo = list(filled_state.get_utxos().keys())[0]
    prev_hash = filled_state.get_block_by_no(filled_state.current_height).hash()

    tx = Transaction(inputs=[TxInput(*an_utxo)], outputs=[TransferOutput(100, bob.pub)])
    signed = SignedTransaction.build_signed(tx, [alice.priv])

    new_block = Block(prev_hash, 0)
    new_block.add_transaction(signed)
    new_block.update_merkle_root()

    filled_state.apply_block(new_block)

    new_utxo = signed.hash(), 0

    with pytest.raises(KeyError):
        filled_state.get_utxo(*an_utxo)

    assert signed.outputs[0] == filled_state.get_utxo(*new_utxo)


def test_does_not_apply_block_when_utxo_does_not_exits(empty_state, restored_state, block_with_minting_tx,
                                                       pending_transaction, alice):
    empty_state.apply_block(block_with_minting_tx)

    init_utxos = empty_state.get_utxos()

    valid_input = list(init_utxos.keys())[0]
    valid_transaction = SignedTransaction(Transaction(inputs=[TxInput(*valid_input)], outputs=[]), signatures=[b'beef'])

    invalid_block = next_empty_block(empty_state)
    invalid_block.add_transaction(valid_transaction)
    invalid_block.add_transaction(pending_transaction)
    invalid_block.update_merkle_root()

    with pytest.raises(KeyError):
        empty_state.apply_block(invalid_block)

    assert empty_state.get_utxos() == init_utxos
    with pytest.raises(KeyError):
        empty_state.get_block_by_no(2)

    with restored_state as state:
        assert init_utxos == state.get_utxos()
        with pytest.raises(KeyError):
            state.get_block_by_no(2)


def test_can_get_transaction_by_hash(filled_state):
    tx = filled_state.get_block_by_no(1).transactions[0]

    assert tx == filled_state.get_transaction(tx.hash())


def test_cannot_apply_transaction_with_the_same_hash_twice(filled_state, utxo, alice, minting_transaction):
    next_block = next_empty_block(filled_state)
    next_block.add_transaction(minting_transaction)
    next_block.update_merkle_root()

    filled_state.apply_block(next_block)

    another_block = next_empty_block(filled_state)
    another_block.add_transaction(minting_transaction)
    another_block.update_merkle_root()

    with pytest.raises(TxOverwriteError):
        filled_state.apply_block(another_block)


def test_stores_offer_transaction_and_its_deposit(filled_state, utxo, alice, restored_state, offer_transaction):
    next_block = next_empty_block(filled_state)

    next_block.add_transaction(offer_transaction)
    next_block.update_merkle_root()

    filled_state.apply_block(next_block)

    assert utxo not in filled_state.get_utxos()
    assert utxo not in filled_state.get_dutxos()

    assert (offer_transaction.hash(), 0) in filled_state.get_utxos()
    assert (offer_transaction.hash(), 0) not in filled_state.get_dutxos()

    assert (offer_transaction.hash(), 1) not in filled_state.get_utxos()
    assert (offer_transaction.hash(), 1) in filled_state.get_dutxos()

    assert offer_transaction.hash() in filled_state.get_active_offers()

    with restored_state as state:
        assert offer_transaction.hash() in state.get_active_offers()


def test_stores_offer_match(filled_state, offer_transaction, match_transaction, second_utxo):
    next_block = next_empty_block(filled_state)
    next_block.add_transaction(offer_transaction)
    next_block.update_merkle_root()
    filled_state.apply_block(next_block)

    next_block = next_empty_block(filled_state)

    next_block.add_transaction(match_transaction)
    next_block.update_merkle_root()

    assert second_utxo in filled_state.get_utxos()

    filled_state.apply_block(next_block)

    assert second_utxo not in filled_state.get_utxos()
    assert second_utxo not in filled_state.get_dutxos()

    assert (match_transaction.hash(), 0) in filled_state.get_utxos()
    assert (match_transaction.hash(), 0) not in filled_state.get_dutxos()

    assert (match_transaction.hash(), 1) not in filled_state.get_utxos()
    assert (match_transaction.hash(), 1) in filled_state.get_dutxos()

    assert offer_transaction.hash() not in filled_state.get_active_offers()

    match = filled_state.get_matched_offers()[offer_transaction.hash()]

    assert (offer_transaction.transaction, match_transaction.transaction, next_block.timestamp) == match


def test_persists_offer_match(filled_state, offer_transaction, match_transaction, second_utxo, restored_state):
    next_block = next_empty_block(filled_state)
    next_block.add_transaction(offer_transaction)
    next_block.update_merkle_root()
    filled_state.apply_block(next_block)

    next_block = next_empty_block(filled_state)

    next_block.add_transaction(match_transaction)
    next_block.update_merkle_root()

    filled_state.apply_block(next_block)

    with restored_state as state:
        assert second_utxo not in state.get_utxos()
        assert second_utxo not in state.get_dutxos()

        assert (match_transaction.hash(), 0) in state.get_utxos()
        assert (match_transaction.hash(), 0) not in state.get_dutxos()

        assert (match_transaction.hash(), 1) not in state.get_utxos()
        assert (match_transaction.hash(), 1) in state.get_dutxos()

        assert offer_transaction.hash() not in state.get_active_offers()

        match = state.get_matched_offers()[offer_transaction.hash()]

        assert (offer_transaction.transaction, match_transaction.transaction, next_block.timestamp) == match


def test_confirms_exchange(filled_state_with_matched_offer, offer_transaction, match_transaction,
                           confirmation_transaction):
    state = filled_state_with_matched_offer

    next_block = next_empty_block(state)
    next_block.add_transaction(confirmation_transaction)
    next_block.update_merkle_root()

    state.apply_block(next_block)

    assert (match_transaction.hash(), 1) not in state.get_dutxos()
    assert (offer_transaction.hash(), 1) not in state.get_dutxos()

    assert (match_transaction.hash(), 0) not in state.get_utxos()
    assert (offer_transaction.hash(), 0) not in state.get_utxos()

    assert (match_transaction.hash(), 1) in state.get_utxos()
    assert (offer_transaction.hash(), 1) in state.get_utxos()

    assert offer_transaction.hash() not in state.get_active_offers()
    assert offer_transaction.hash() not in state.get_matched_offers()


def test_persists_confirmations(filled_state_with_matched_offer, offer_transaction, match_transaction,
                                confirmation_transaction, restored_state):
    state = filled_state_with_matched_offer

    next_block = next_empty_block(state)
    next_block.add_transaction(confirmation_transaction)
    next_block.update_merkle_root()

    state.apply_block(next_block)

    with restored_state as state:
        assert (offer_transaction.hash(), 1) not in state.get_dutxos()
        assert (match_transaction.hash(), 1) not in state.get_dutxos()

        assert (offer_transaction.hash(), 0) not in state.get_utxos()
        assert (match_transaction.hash(), 0) not in state.get_utxos()

        assert (offer_transaction.hash(), 1) in state.get_utxos()
        assert (match_transaction.hash(), 1) in state.get_utxos()

        assert offer_transaction.hash() not in state.get_active_offers()
        assert offer_transaction.hash() not in state.get_matched_offers()


def test_unlocks_deposits(filled_state_with_matched_offer, offer_transaction, match_transaction,
                          unlocking_transactions):
    state = filled_state_with_matched_offer

    unlocking1, unlocking2 = unlocking_transactions

    next_block = next_empty_block(state)
    next_block.add_transaction(unlocking1)  # NOTE: we here unlock the other side comparing to the prev test
    next_block.update_merkle_root()

    state.apply_block(next_block)

    assert (offer_transaction.hash(), 1) not in state.get_dutxos()
    assert (match_transaction.hash(), 1) not in state.get_dutxos()

    assert (offer_transaction.hash(), 0) not in state.get_utxos()
    assert (match_transaction.hash(), 0) not in state.get_utxos()

    assert (offer_transaction.hash(), 1) in state.get_utxos()
    assert (match_transaction.hash(), 1) not in state.get_utxos()

    assert offer_transaction.hash() not in state.get_active_offers()
    assert offer_transaction.hash() not in state.get_matched_offers()


def test_persists_unlocking_deposits(filled_state_with_matched_offer, offer_transaction, match_transaction,
                                     unlocking_transactions, restored_state):
    state = filled_state_with_matched_offer

    unlocking1, unlocking2 = unlocking_transactions

    next_block = next_empty_block(state)
    next_block.add_transaction(unlocking2)
    next_block.update_merkle_root()

    state.apply_block(next_block)

    with restored_state as state:
        assert (offer_transaction.hash(), 1) not in state.get_dutxos()
        assert (match_transaction.hash(), 1) not in state.get_dutxos()

        assert (offer_transaction.hash(), 0) not in state.get_utxos()
        assert (match_transaction.hash(), 0) not in state.get_utxos()

        assert (offer_transaction.hash(), 1) not in state.get_utxos()
        assert (match_transaction.hash(), 1) in state.get_utxos()

        assert offer_transaction.hash() not in state.get_active_offers()
        assert offer_transaction.hash() not in state.get_matched_offers()
