import time
from threading import Thread

from termcolor import colored

from chasm.maintenance.logger import Logger
from chasm.services_manager import Service
from chasm.state.state import State


class Miner(Service):

    def __init__(self, state: State, miner_address: bytes, block_interval: int):
        self._state = state
        self._block_interval = block_interval
        self._miner = miner_address

        self._thread = Thread(target=self, name=Miner.__name__)
        self._exit_condition = None

        self._logger = Logger('chasm.miner')

    def __call__(self, *args, **kwargs):
        while True:
            try:
                self._logger.info('\U00002692 ' + colored(' Mined new block', 'green'))
                self._logger.info('\U000026D3 ' + colored(' Successfully applied new block', "green"))
            except KeyError as error:
                self._logger.error(str(error))
            for i in range(100):
                time.sleep(self._block_interval / 100)
                if self._exit_condition():
                    return

    def start(self, exit_condition):
        self._exit_condition = exit_condition
        self._thread.start()
        return True

    def stop(self):
        self._thread.join()

    def is_running(self):
        return self._thread.is_alive()

