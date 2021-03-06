"""Client for running commands on node"""

import argparse

from chasm import rpc
from chasm.consensus import Side
from chasm.maintenance.config import Config, DEFAULT_CONFIG_FILE
from chasm.maintenance.logger import Logger
from chasm.rpc import list_token_names, TIMEOUT_FORMAT, ALL_ADDRESSES
from chasm.rpc.client import show_transaction, show_balance, generate_account, \
    create_offer, accept_offer, unlock_deposit, transfer, \
    show_keys, show_marketplace, show_matches, show_accepted_offers, show_all_funds, \
    build_tx, xpeer_transfer, sign, send, show_dutxos, show_utxos, confirm


# pylint: disable=missing-docstring
def get_parser():
    parser = argparse.ArgumentParser(description='Chasm client',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-n', '--node', required=False, help="hostname")

    parser.add_argument('-p', "--port", required=False, help="port")

    parser.add_argument('-d', '--datadir', required=False, help="datadir for chasm storage")

    parser.add_argument('-c', '--config', required=False, help='config file')

    create_subparsers(parser.add_subparsers())

    parser.set_defaults(func=lambda x: parser.print_help())

    return parser


def create_subparsers(subparsers):
    create_balance_parser(subparsers)
    create_confirm_parser(subparsers)
    create_build_parser(subparsers)
    create_dutxo_parser(subparsers)
    create_funds_parser(subparsers)
    create_gen_address_parser(subparsers)
    create_keys_parser(subparsers)
    create_marketplace_parser(subparsers)
    create_match_parser(subparsers)
    create_matches_parser(subparsers)
    create_offer_parser(subparsers)
    create_offers_parser(subparsers)
    create_send_tx_parser(subparsers)
    create_sign_parser(subparsers)
    create_show_tx_parser(subparsers)
    create_transfer_parser(subparsers)
    create_unlock_parser(subparsers)
    create_utxo_parser(subparsers)
    create_xpeer_parser(subparsers)


def create_marketplace_parser(subparsers):
    parser = subparsers.add_parser('marketplace',
                                   description="show all current offers, \
                                    possible tokens: {}".format(list_token_names()))
    parser.add_argument('--token', default="all",
                        help="currency for sale")
    parser.add_argument('--expected', default="all",
                        help="payment currency")
    parser.set_defaults(func=show_marketplace)


def create_show_tx_parser(subparsers):
    parser = subparsers.add_parser('show',
                                   description="show transaction")
    parser.add_argument('--tx', help="hash of the transaction",
                        required=True)
    parser.set_defaults(func=show_transaction)


def create_send_tx_parser(subparsers):
    parser = subparsers.add_parser('send',
                                   description="show transaction")
    parser.add_argument('--tx', help="hash of the transaction",
                        required=True)
    parser.add_argument('--signatures', default=[], nargs='*',
                        help="list of signatures")

    parser.set_defaults(func=send)


def create_confirm_parser(subparsers):
    parser = subparsers.add_parser('confirm',
                                   description="confirm exchange")
    parser.add_argument('--address', help="address for income",
                        required=True)
    parser.add_argument('--exchange', help="exchange (hash of the offer)",
                        required=True)
    parser.add_argument('--proof_in', help="proof of offer maker's transfer(tx hash)",
                        required=True)

    parser.add_argument('--proof_out', help="proof of offer taker's transfer(tx hash)",
                        required=True)

    parser.set_defaults(func=confirm)


def create_sign_parser(subparsers):
    parser = subparsers.add_parser('sign',
                                   description="sign transaction")
    parser.add_argument('--tx', help="hash of the transaction",
                        required=True)
    parser.add_argument('--address', help="address of signer",
                        required=True)
    parser.set_defaults(func=sign)


def create_balance_parser(subparsers):
    parser = subparsers.add_parser('balance',
                                   description="show balance of the account")
    parser.add_argument('--address', required=True,
                        help="address")
    parser.set_defaults(func=show_balance)


def create_dutxo_parser(subparsers):
    parser = subparsers.add_parser('dutxo',
                                   description="show DUTXOs of the account")
    parser.add_argument('--address', required=True,
                        help="address")
    parser.set_defaults(func=show_dutxos)


def create_utxo_parser(subparsers):
    parser = subparsers.add_parser('utxo',
                                   description="show UTXOs of the account")
    parser.add_argument('--address', required=True,
                        help="address")
    parser.set_defaults(func=show_utxos)


def create_build_parser(subparsers):
    parser = subparsers.add_parser('build',
                                   description="build any transaction from json file")
    parser.add_argument('--file', required=True,
                        help="path to json file with transaction")
    parser.set_defaults(func=build_tx)


def create_funds_parser(subparsers):
    parser = subparsers.add_parser('funds',
                                   description="show balance of all accounts")
    parser.set_defaults(func=show_all_funds)


def create_gen_address_parser(subparsers):
    parser = subparsers.add_parser('generate',
                                   description="generate new address")
    parser.set_defaults(func=generate_account)


def create_offer_parser(subparsers):
    parser = subparsers.add_parser('offer',
                                   description="create an exchange offer")
    parser.add_argument('--address', required=True,
                        help='address of offer maker(xpc)')
    parser.add_argument('--token', required=True,
                        help="Currency being sold, \
                                    possible tokens: {}"
                        .format(list_token_names()))
    parser.add_argument('--amount', required=True, type=int,
                        help="amount of token being sold(smallest denomination")
    parser.add_argument('--expected', required=True,
                        help="expected incoming currency, \
                                    possible tokens: {}"
                        .format(list_token_names()))
    parser.add_argument('--price', required=True, type=int,
                        help='price of offered tokens')
    parser.add_argument('--receive', required=True,
                        help='receive payment address')
    parser.add_argument('--confirmation', required=True, type=int,
                        help='confirmation fee(bdzys)')
    parser.add_argument('--deposit', required=True, type=int,
                        help='deposit fee(bdzys)')
    parser.add_argument('--timeout', required=True,
                        help='offer timeout, format: {}'
                        .format(TIMEOUT_FORMAT.replace("%", "")))
    parser.add_argument('--fee', required=True, type=int,
                        help="transaction fee(bdzys)")
    parser.set_defaults(func=create_offer)


def create_offers_parser(subparsers):
    parser = subparsers.add_parser('offers',
                                   description="show accepted offers")
    parser.add_argument('--address', default=ALL_ADDRESSES,
                        help="address for income")
    parser.set_defaults(func=show_accepted_offers
                        )


def create_match_parser(subparsers):
    parser = subparsers.add_parser('match',
                                   description="accept the offer")
    parser.add_argument('--offer', required=True,
                        help="hash of the offer")
    parser.add_argument('--address', required=True,
                        help='address of offer taker(xpc)')
    parser.add_argument('--receive', required=True,
                        help='receive payment address')
    parser.add_argument('--confirmation', required=True, type=int,
                        help='confirmation fee(bdzys)')
    parser.add_argument('--deposit', required=True, type=int,
                        help='deposit fee(bdzys)')
    parser.add_argument('--fee', required=True, type=int,
                        help="transaction fee(bdzys)")
    parser.set_defaults(func=accept_offer)


def create_matches_parser(subparsers):
    parser = subparsers.add_parser('matches',
                                   description="show offer matches")
    parser.add_argument('--address', default=ALL_ADDRESSES,
                        help="address for income")
    parser.set_defaults(func=show_matches)


def create_unlock_parser(subparsers):
    parser = subparsers.add_parser('unlock',
                                   description="unlock the deposit")
    parser.add_argument('--offer', required=True,
                        help="hash of the offer")
    parser.add_argument('--address', required=True,
                        help='address of requestor(xpc)')
    parser.add_argument('--deposit', required=True, type=int,
                        help='deposit fee(bdzys)')
    parser.add_argument('--fee', required=True, type=int,
                        help="transaction fee(bdzys)")
    parser.add_argument('--side', required=True, type=int,
                        help="side of the exchange: maker({}), taker({})"
                        .format(Side.OFFER_MAKER.value,
                                Side.OFFER_TAKER.value))
    parser.add_argument('--proof', required=True,
                        help='proof of honesty(hex)')
    parser.set_defaults(func=unlock_deposit)


def create_transfer_parser(subparsers):
    parser = subparsers.add_parser('transfer',
                                   description="transfer funds")
    parser.add_argument('--fee', required=True, type=int,
                        help="transaction fee(in bdzys denomination)")
    parser.add_argument('--owner', required=True,
                        help="owner address")
    parser.add_argument('--value', required=True, type=int,
                        help="amount to be transferred(bdzys)")
    parser.add_argument('--receiver', required=True,
                        help="receiver address")

    parser.set_defaults(func=transfer)


def create_xpeer_parser(subparsers):
    parser = subparsers.add_parser('xpeer',
                                   description="transfer xpc as a part of an exchange")
    parser.add_argument('--fee', required=True, type=int,
                        help="transaction fee(in bdzys denomination)")
    parser.add_argument('--owner', required=True,
                        help="owner address")
    parser.add_argument('--value', required=True, type=int,
                        help="amount to be transferred(bdzys)")
    parser.add_argument('--receiver', required=True,
                        help="receiver address")
    parser.add_argument('--offer', required=True,
                        help="offer hash")

    parser.set_defaults(func=xpeer_transfer)


def create_keys_parser(subparsers):
    parser = subparsers.add_parser('keys',
                                   description="show all addresses from datadir")
    parser.set_defaults(func=show_keys)


def _prepare_config(args):
    overridden = {}
    if args.datadir:
        overridden['datadir'] = args.datadir
    if args.node:
        overridden['node'] = args.node
    if args.port:
        overridden['rpc_port'] = args.port

    return Config(args.config or DEFAULT_CONFIG_FILE, overridden=overridden)


def main():
    """
    Main function, runs client side
    """

    parser = get_parser()
    args = parser.parse_args()

    config = _prepare_config(args)
    Logger.level = config.get('logger_level')

    logger = Logger('chasm.cli.rpc')
    rpc.client.logger = logger

    args.node = config.get('node')
    args.port = config.get('rpc_port')
    args.datadir = config.get('datadir')

    try:
        args.func(args)
    except RuntimeError:
        logger.exception("An error occurred!")
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt")


if __name__ == "__main__":
    main()
