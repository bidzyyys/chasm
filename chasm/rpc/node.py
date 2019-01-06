"""RPC Server"""

from jsonrpc import JSONRPCResponseManager, dispatcher
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response

from chasm.serialization.json_serializer import JSONSerializer
from chasm.serialization.rlp_serializer import RLPSerializer
from . import logger

# pylint: disable=invalid-name

json_serializer = JSONSerializer()
rlp_serializer = RLPSerializer()


@dispatcher.add_method
def get_utxos(address):
    """
    Return UTXOs of given address
    :param address: address
    :return: list of UTXOs
    """
    # TODO
    logger.info("Getting UTXOs of: %s", address)
    return [
        {
            "tx_hash": b'Tests'.hex(),
            "output_no": 69,
            "value": 1000
        }
    ]


@dispatcher.add_method
def get_current_offers():
    """
    Return all current offers
    :return:
    """
    # TODO
    logger.info("Getting current offers")
    return []


@dispatcher.add_method
def get_tx(tx_hash):
    pass


@dispatcher.add_method
def publish_transaction(tx_hex):
    print(tx_hex)
    signed_tx = json_serializer.decode(tx_hex)
    # print("{} :{}".format(type(signed_tx).__name__,
    #                       json_serializer.encode(signed_tx)))
    # # TODO
    return True


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
