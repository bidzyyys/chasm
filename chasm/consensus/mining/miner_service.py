import time
from threading import Thread

from termcolor import colored

from chasm.consensus.mining.block_builder import BlockBuilder
from chasm.consensus.mining.miner import Miner
from chasm.maintenance.logger import Logger
from chasm.services_manager import Service
from chasm.state.state import State


class MinerService(Service):
    WORKER_STEP = 10

    def __init__(self, state: State, miner_address: bytes, block_interval: int, workers: int):
        self._state = state
        self._block_interval = block_interval
        self._workers = workers

        self._builder = BlockBuilder(state, miner_address)

        self._thread = Thread(target=self, name=MinerService.__name__)
        self._exit_condition = None

        self._logger = Logger('chasm.miner')

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

        return None
