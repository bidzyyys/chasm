import time
from threading import Thread

from termcolor import colored

from chasm.consensus.mining.block_builder import BlockBuilder
from chasm.consensus.mining.miner import Miner
from chasm.maintenance.config import Config
from chasm.maintenance.logger import Logger
from chasm.services_manager import Service
from chasm.state.service import StateService


class MinerService(Service):
    WORKER_STEP = 10

    def __init__(self, state: StateService, config: Config):
        self._state = state
        self._config = config
        self._thread = Thread(target=self, name=MinerService.__name__)

        self._builder = None
        self._workers = None

        self._exit_condition = None
        self._logger = None

    def __call__(self, *args, **kwargs):

        time.sleep(1)  # gives time to other services to fully start

        while not self._exit_condition():

            self._logger.info('Building new block')
            block = self._builder.build_block()
            self._logger.info(f'Successfully built a new block with {block.transactions.__len__()} transactions.')

            nonce = self._mine(block)
            if nonce:
                block.header.set_nonce(nonce)
                self._logger.info('\U00002692 ' + colored(f' Mined new block with hash {block.hash().hex()}', 'yellow'))

                self._state.apply_block(block)
                self._logger.info('\U000026D3 ' + colored(
                    f' Successfully applied the new block at height {self._state.current_height}', "green"))

    def start(self, exit_condition):

        miner = self._config.get('xpeer_miner_address')

        self._logger = Logger('chasm.miner')

        self._builder = BlockBuilder(self._state, miner)
        self._workers = self._config.get('xpeer_miner_threads')

        self._exit_condition = exit_condition
        self._thread.start()
        return True

    def stop(self):
        self._thread.join()

    def is_running(self):
        return self._thread.is_alive()

    def _mine(self, block):

        searched_nonces = 0

        while not self._exit_condition():
            workers = []
            for i in range(self._workers):
                miner = Miner(block.header)
                worker_range = range(searched_nonces, searched_nonces + MinerService.WORKER_STEP)
                thread = Thread(target=lambda: miner.check_nonce_in_range(worker_range))
                searched_nonces += MinerService.WORKER_STEP
                workers.append((miner, thread))
                thread.start()

            for _, thread in workers:
                thread.join()

            for miner, _ in workers:
                if miner.result:
                    return miner.result

            self._logger.debug(colored(f'Searched through up to: {searched_nonces}', "blue"))

        return None
