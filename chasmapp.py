"""Full node app"""

import argparse

from chasm import startup
from chasm.logger.logger import get_logger
from chasm.rpc.node import run


# pylint: disable=missing-docstring
def get_parser(config):
    parser = argparse.ArgumentParser(description='Node app',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-p', "--port", default=config.getint('RPC', 'port'),
                        help="port")

    parser.add_argument('-d', '--datadir', default=config.get('DEFAULT', 'data_dir'),
                        help="datadir for chasm storage")
    return parser


def main():
    """
    Main function, runs server side
    """

    config = startup.get_config()

    parser = get_parser(config)
    args = parser.parse_args()

    logger = get_logger("chasm-app", config.get('LOGGER', 'level'))

    try:
        run(port=args.port, data_dir=args.datadir)

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt")
    except BaseException:
        logger.error("Unexpected exception:", exc_info=True)


if __name__ == "__main__":
    main()
