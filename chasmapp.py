"""Full node app"""

import argparse
import os

from chasm.consensus.mining.miner_service import MinerService
from chasm.maintenance.config import Config
from chasm.maintenance.logger import Logger
from chasm.rpc.node import RPCServerService
from chasm.services_manager import LazyService, ServicesManager
from chasm.state.state import State


def get_parser(config):
    parser = argparse.ArgumentParser(description='Node app',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-p', "--port", default=config.rpc_port(),
                        help="port")

    parser.add_argument('-d', '--datadir', default=config.data_dir(),
                        help="datadir for chasm storage")
    return parser


def main():
    """
    Main function, runs server side
    """

    config = Config()

    parser = get_parser(config)
    args = parser.parse_args()

    Logger.level = config.logger_level()

    services = [
        LazyService('state', State, db_dir=os.path.join(args.datadir, 'db'), pending_queue_size=config.pending_txs()),
        LazyService('rpc_server', RPCServerService, port=config.rpc_port(), required_services=['state']),
        LazyService('miner', MinerService, miner_address=config.miner(), block_interval=config.block_interval(),
                    workers=config.mining_workers(), required_services=['state'])
    ]

    with ServicesManager(services) as manager:
        manager.run()

    exit()


if __name__ == "__main__":
    main()
