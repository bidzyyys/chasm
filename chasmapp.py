"""Full node app"""

import argparse

from chasm.consensus.mining.miner_service import MinerService
from chasm.maintenance.config import Config, DEFAULT_CONFIG_FILE
from chasm.maintenance.logger import Logger
from chasm.rpc.node import RPCServerService
from chasm.services_manager import LazyService, ServicesManager
from chasm.state.service import StateService


def get_parser():
    parser = argparse.ArgumentParser(description='Node app',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-p', "--port", help="port")

    parser.add_argument('-d', '--datadir', help="datadir for chasm storage")

    parser.add_argument('-c', '--config', help="path to config file")

    parser.add_argument('--dev', action='store_true')

    return parser


def _prepare_config(args):
    overridden = {}
    if args.datadir:
        overridden['datadir'] = args.datadir
    if args.port:
        overridden['rpc_port'] = args.port

    return Config(args.config or DEFAULT_CONFIG_FILE, overridden=overridden)


def main():
    """
    Main function, runs server side
    """

    parser = get_parser()

    args = parser.parse_args()

    config = _prepare_config(args)

    Logger.level = config.get('logger_level')

    services = [
        LazyService('state', StateService, dev=args.dev, config=config),
        LazyService('rpc_server', RPCServerService, config=config, required_services=['state']),
        LazyService('miner', MinerService, dev=args.dev, config=config, required_services=['state'])
    ]

    with ServicesManager(services) as manager:
        manager.run()

    exit()


if __name__ == "__main__":
    main()
