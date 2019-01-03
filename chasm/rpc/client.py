"""RPC Client"""

import json

import requests

from . import logger


def generate_account(args):
    print(__name__ + str(args))


def show_transaction(args):
    print(__name__ + str(args))


def transfer(args):
    print(__name__ + str(args))


def create_offer(args):
    print(__name__ + str(args))


def accept_offer(args):
    print(__name__ + str(args))


def unlock_deposit(args):
    print(__name__ + str(args))


def get_balance(args):
    print(__name__ + str(args))


def show_account_history(args):
    print(__name__ + str(args))


def show_address(args):
    print(__name__ + str(args))


def run(host, port, payload):
    url = "http://{}:{}/jsonrpc".format(host, port)
    headers = {'content-type': 'application/json'}

    # Example echo method
    # payload = {
    #     "method": "dupa",
    #     "params": ["echome!"],
    #     "jsonrpc": "2.0",
    #     "id": 0,
    # }
    response = requests.post(
        url, data=json.dumps(payload), headers=headers).json()

    logger.info("Response: " + str(response))

    return response
