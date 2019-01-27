import os

from chasm.consensus.validation.block_validator import BlockValidator, DIFFICULTY_COMPUTATION_INTERVAL
from chasm.consensus.validation.tx_validator import TxValidator
from chasm.maintenance.config import Config
from chasm.services_manager import Service
from chasm.state.state import State


class StateService(Service):
    def __init__(self, config: Config, dev=False):
        self._state: State = None
        self._config = config
        self._dev = dev

    def start(self, _stop_condition):
        db_dir = os.path.join(self._config.get('datadir'), 'db')
        self._state = State(db_dir, self._config.get('xpeer_pending_txs'))
        return True

    def is_running(self):
        return not self._state.db.is_closed()

    def stop(self):
        self._state.close()

    def apply_block(self, block):
        self._build_block_validator().validate(block)
        self._state.apply_block(block)

    def add_pending_tx(self, tx):
        self._build_tx_validator().validate(tx)
        self._state.add_pending_tx(tx)

    def __getattribute__(self, item):
        try:
            return Service.__getattribute__(self, item)
        except AttributeError:
            return getattr(self._state, item)

    def _build_block_validator(self):
        height = self._state.current_height

        old_block_no = 0 if height - DIFFICULTY_COMPUTATION_INTERVAL < 0 else height - DIFFICULTY_COMPUTATION_INTERVAL
        last_block = self._state.get_block_by_no(height)
        old_block = self._state.get_block_by_no(old_block_no)

        return BlockValidator(self._state.get_utxos(), self._state.get_active_offers(),
                              self._state.get_matched_offers(), last_block.header, old_block.header, height, dev=self._dev)

    def _build_tx_validator(self):
        return TxValidator(self._state.get_utxos(), self._state.get_active_offers(), self._state.get_matched_offers())
