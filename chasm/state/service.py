import os

from chasm.maintenance.config import Config
from chasm.services_manager import Service
from chasm.state.state import State


class StateService(Service):
    def __init__(self, config: Config):
        self._state: State = None
        self._config = config

    def start(self, _stop_condition):
        db_dir = os.path.join(self._config.get('datadir'), 'db')
        self._state = State(db_dir, self._config.get('xpeer_pending_txs'))
        return True

    def is_running(self):
        return not self._state.db.is_closed()

    def stop(self):
        self._state.close()

    def __getattribute__(self, item):
        try:
            return Service.__getattribute__(self, item)
        except AttributeError:
            return getattr(self._state, item)
