from chasm.consensus import Block
from chasm.consensus.primitives.transaction import MintingTransaction
from chasm.consensus.primitives.tx_output import TransferOutput
from chasm.state.state import State


class BlockBuilder:

    def __init__(self, state: State, miner: bytes):
        self._state: State = state
        self._miner: bytes = miner
        self.prev = self._state.get_block_by_no(self._state.current_height).hash()

    def build_block(self) -> Block:
        txs = [self._get_minting_tx()]

        prev_hash = self._state.get_block_by_no(self._state.current_height).hash()

        block = Block(previous_block_hash=prev_hash, difficulty=0, transactions=txs)

        block.update_merkle_root()

        return block

    def _get_minting_tx(self) -> MintingTransaction:
        output = TransferOutput(10 ** 20, self._miner)
        return MintingTransaction(outputs=[output], height=self._state.current_height)
