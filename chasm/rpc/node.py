"""RPC Server"""

from jsonrpc import JSONRPCResponseManager, dispatcher
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response

from . import logger


@dispatcher.add_method
def get_utxos(address):
    pass


@dispatcher.add_method
def get_tx(tx_hash):
    pass


@dispatcher.add_method
def transfer():
    pass


@dispatcher.add_method
def create_offer():
    pass


@dispatcher.add_method
def accept_offer():
    pass


@dispatcher.add_method
def unlock_deposit():
    pass


@dispatcher.add_method
def get_account_history(address):
    pass


@Request.application
def application(request):
    response = JSONRPCResponseManager.handle(
        request.data, dispatcher)
    return Response(response.json, mimetype='application/json')


def run(host, port):
    run_simple(host, port, application)
