"""Full node app"""

import argparse

from chasm.logger.logger import get_logger
from chasm.rpc.node import run


def get_parser():
    parser = argparse.ArgumentParser(description='Node app',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-n', '--node', default="127.0.0.1",
                        help="hostname")

    parser.add_argument('-p', "--port", default=6969,
                        help="port")

    parser.add_argument('-d', '--datadir', default="~/.chasm",
                        help="datadir for chasm storage")

    return parser


def main():
    """
    Main function, runs server side
    """
    logger = get_logger("chasmcli")
    parser = get_parser()
    args = parser.parse_args()

    try:
        run(host=args.node,
            port=args.port)

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt")
    except BaseException:
        logger.error("Unexpected exception:", exc_info=True)


if __name__ == "__main__":
    main()
