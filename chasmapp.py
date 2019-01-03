"""Full node app"""

import argparse

from chasm.logger.logger import get_logger
from chasm.rpc.node import run

PARSER = argparse.ArgumentParser(description='Node app',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

PARSER.add_argument('-n', '--node', default="127.0.0.1",
                    help="hostname")

PARSER.add_argument('-p', "--port", default=6969,
                    help="port")


def main():
    """
    Main function, runs server side
    """
    logger = get_logger("chasmcli")
    args = PARSER.parse_args()

    try:
        run(host=args.node,
            port=args.port)

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt")
    except BaseException:
        logger.error("Unexpected exception:", exc_info=True)


if __name__ == "__main__":
    main()
