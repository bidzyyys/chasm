"""Full node app"""

import argparse
import os
import time

from chasm.config import Config
from chasm.consensus.blockchain.service import Miner
from chasm.logger.logger import get_logger
# pylint: disable=missing-docstring
from chasm.server.services_manager import ServicesManager
from chasm.state.state import State


def get_parser(config):
    parser = argparse.ArgumentParser(description='Node app',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-p', "--port", default=config.rpc_port(),
                        help="port")

    parser.add_argument('-d', '--datadir', default=config.data_dir(),
                        help="datadir for chasm storage")
    return parser


def get_services(config):
    def _get_logger(name):
        return get_logger(name, config.logger_level())

    db_dir = os.path.join(config.data_dir(), 'db')

    state = State(db_dir, config.pending_txs())
    miner = Miner(state, config.miner(), config.block_interval(), _get_logger('chasm.miner'))

    return [state, miner]


def main():
    """
    Main function, runs server side
    """

    config = Config()

    parser = get_parser(config)
    args = parser.parse_args()

    logger = get_logger("chasm.app", config.logger_level())

    with ServicesManager(get_services(config), get_logger("chasm.manager", config.logger_level())):
        while True:
            time.sleep(10)


# try:
#     run(port=args.port, data_dir=args.datadir)
# except KeyboardInterrupt:
#     logger.info("Keyboard interrupt")
# except BaseException:
#     logger.error("Unexpected exception:", exc_info=True)


if __name__ == "__main__":
    main()
