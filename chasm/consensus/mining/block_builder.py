from chasm.consensus import Block
from chasm.consensus.primitives.transaction import MintingTransaction
from chasm.consensus.primitives.tx_output import TransferOutput
from chasm.consensus.validation.block_validator import DIFFICULTY_COMPUTATION_INTERVAL, \
    BlockStatelessValidator
from chasm.state.service import StateService
from chasm.state.state import State


class BlockBuilder:

    def __init__(self, state: StateService, miner: bytes):
        self._state: State = state
        self._miner: bytes = miner

    def build_block(self) -> Block:
        # utxos = self._state.get_utxos()
        # offers = self._state.get_active_offers()
        # accepted_offers = self._state.get_accepted_offers()

        current_height = self._state.current_height
        last_block = self._state.get_block_by_no(current_height)

        old_block_height = current_height - DIFFICULTY_COMPUTATION_INTERVAL
        old_block = self._state.get_block_by_no(old_block_height if old_block_height > 0 else 0)

        # validator = BlockValidator(utxos, offers, accepted_offers, last_block.header, old_block.header, current_height)

        minted_value = BlockStatelessValidator.get_minting_value(current_height + 1)
        difficulty = BlockStatelessValidator.get_expected_difficulty(current_height + 1, last_block.difficulty,
                                                                     old_block.timestamp, last_block.timestamp)

        txs = [self._get_minting_tx(minted_value)]

        block = Block(previous_block_hash=last_block.hash(), difficulty=difficulty, transactions=txs)

        block.update_merkle_root()

        return block

    def _get_minting_tx(self, value) -> MintingTransaction:
        output = TransferOutput(value, self._miner)
        return MintingTransaction(outputs=[output], height=self._state.current_height)
