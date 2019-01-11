import time
from logging import Logger
from threading import Thread

from termcolor import colored

from chasm.services_manager import Service
from chasm.state.state import State


class Miner(Service):
    def __init__(self, state: State, miner_address: bytes, block_interval: int, logger: Logger):
        self._state = state
        self._block_interval = block_interval
        self._miner = miner_address

        self._thread = Thread(target=self, name=Miner.__name__)

        self._logger = logger

    def __call__(self, *args, **kwargs):
        while not self._exit_condition():
            try:
                time.sleep(1)
                self._logger.info('\U00002692' + colored(' Mined new block', 'green'))
                self._logger.info('\U000026D3' + colored(' Successfully applied new block', "green"))
            except KeyError as error:
                self._logger.error(str(error))

        self._logger.info("Stopping")

    def __start__(self, exit_condition):
        self._exit_condition = exit_condition
        self._thread.start()

    def __stop__(self):
        self._thread.join()
