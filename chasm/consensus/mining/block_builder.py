import queue

from chasm.consensus import Block
from chasm.consensus.primitives.transaction import MintingTransaction
from chasm.consensus.primitives.tx_output import TransferOutput
from chasm.consensus.validation.block_validator import DIFFICULTY_COMPUTATION_INTERVAL, \
    BlockStatelessValidator
from chasm.serialization.rlp_serializer import RLPSerializer
from chasm.state.service import StateService
from chasm.state.state import State


class BlockBuilder:

    def __init__(self, state: StateService, miner: bytes):
        self._state: State = state
        self._miner: bytes = miner

    def build_block(self) -> Block:

        current_height = self._state.current_height
        last_block = self._state.get_block_by_no(current_height)

        old_block_height = current_height - DIFFICULTY_COMPUTATION_INTERVAL
        old_block = self._state.get_block_by_no(old_block_height if old_block_height > 0 else 0)

        minted_value = BlockStatelessValidator.get_minting_value(current_height + 1)
        difficulty = BlockStatelessValidator.get_expected_difficulty(current_height + 1, last_block.difficulty,
                                                                     old_block.timestamp, last_block.timestamp)

        minting_tx = self._get_minting_tx(minted_value)

        block = Block(previous_block_hash=last_block.hash(), difficulty=difficulty)

        block = self._add_transactions(block, minting_tx)

        block.update_merkle_root()

        return block

    def _get_minting_tx(self, value) -> MintingTransaction:
        output = TransferOutput(value, self._miner)
        return MintingTransaction(outputs=[output], height=self._state.current_height)

    def _add_transactions(self, block, minting_tx):
        utxos = self._state.get_utxos()
        used_utxos = []

        serializer = RLPSerializer()

        minting_output = minting_tx.outputs[0]

        block.add_transaction(minting_tx)

        while not BlockStatelessValidator.check_block_size(len(serializer.encode(block))):
            tx = None
            try:
                tx = self._state.pop_pending_tx()
            except queue.Empty:
                return block

            for tx_input in tx.inputs:
                utxo = (tx_input.tx_hash, tx_input.output_no)
                if utxo in used_utxos or utxo not in utxos:
                    continue
                tx_output = utxos[utxo]
                minting_output.value += tx_output.value

            for tx_output in tx.outputs:
                minting_output.value -= tx_output.value

            block.add_transaction(tx)

        return block
