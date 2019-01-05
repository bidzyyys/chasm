"""Client for running commands on node"""

import argparse

from chasm.logger.logger import get_logger
from chasm.rpc import list_token_names
from chasm.rpc.client import show_transaction, show_balance, generate_account, \
    create_offer, accept_offer, unlock_deposit, transfer, show_account_history, \
    receive, show_marketplace, show_matchings, show_offers, show_all_funds


def get_parser():
    parser = argparse.ArgumentParser(description='Chasm client',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-n', '--node', default="127.0.0.1",
                        help="hostname")

    parser.add_argument('-p', "--port", default=6969,
                        help="port")

    parser.add_argument('-d', '--datadir', default="~/.chasm",
                        help="datadir for chasm storage")

    create_subparsers(parser.add_subparsers())

    return parser


def create_subparsers(subparsers):
    create_balance_parser(subparsers)
    create_funds_parser(subparsers)
    create_gen_address_parser(subparsers)
    create_history_parser(subparsers)
    create_marketplace_parser(subparsers)
    create_match_parser(subparsers)
    create_matchings_parser(subparsers)
    create_offer_parser(subparsers)
    create_offers_parser(subparsers)
    create_receive_parser(subparsers)
    create_show_tx_parser(subparsers)
    create_transfer_parser(subparsers)
    create_unlock_parser(subparsers)


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
    parser.add_argument('tx_hash', help="hash of the transaction")
    parser.set_defaults(func=show_transaction)


def create_balance_parser(subparsers):
    parser = subparsers.add_parser('balance',
                                   description="show balance of the account")
    parser.add_argument('address', help="address")
    parser.set_defaults(func=show_balance)


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
    parser.set_defaults(func=create_offer)


def create_offers_parser(subparsers):
    parser = subparsers.add_parser('offers',
                                   description="show my offers")
    parser.set_defaults(func=show_offers)


def create_match_parser(subparsers):
    parser = subparsers.add_parser('match',
                                   description="accept the offer")
    parser.set_defaults(func=accept_offer)


def create_matchings_parser(subparsers):
    parser = subparsers.add_parser('matchings',
                                   description="show my accepted offers")
    parser.set_defaults(func=show_matchings)


def create_unlock_parser(subparsers):
    parser = subparsers.add_parser('unlock',
                                   description="unlock the deposit")
    parser.set_defaults(func=unlock_deposit)


def create_transfer_parser(subparsers):
    parser = subparsers.add_parser('transfer',
                                   description="transfer funds")
    parser.set_defaults(func=transfer)


def create_history_parser(subparsers):
    parser = subparsers.add_parser('history',
                                   description="show account history")
    parser.set_defaults(func=show_account_history)


def create_receive_parser(subparsers):
    parser = subparsers.add_parser('receive',
                                   description="show all addresses from datadir")
    parser.set_defaults(func=receive)


def main():
    """
    Main function, runs client side
    """
    logger = get_logger("chasmcli")
    parser = get_parser()
    args = parser.parse_args()

    try:
        args.func(args)
    except RuntimeError:
        logger.exception("An error occured!")
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt")


if __name__ == "__main__":
    main()
