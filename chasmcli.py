"""Client for running commands on node"""

import argparse

from chasm.logger.logger import get_logger
from chasm.rpc.client import run

PARSER = argparse.ArgumentParser(description='Client for running commands on chasm node',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

PARSER.add_argument("--host", default="127.0.0.1",
                    help="hostname")

PARSER.add_argument("--port", default=6969,
                    help="port")


def main():
    """
    Main function, runs client side
    """
    logger = get_logger("chasmcli")
    args = PARSER.parse_args()

    try:
        run(host=args.host,
            port=args.port)

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt")
    except BaseException:
        logger.error("Unexpected exception:", exc_info=True)


if __name__ == "__main__":
    main()
