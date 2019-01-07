"""RPC Server"""
from queue import Full

from jsonrpc import JSONRPCResponseManager, dispatcher
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response

from chasm.serialization.json_serializer import JSONSerializer
from chasm.serialization.rlp_serializer import RLPSerializer
from chasm.state.state import State
from . import logger, ALL

# pylint: disable=invalid-name

json_serializer = JSONSerializer()
rlp_serializer = RLPSerializer()

state = State()


def filter_txos(txos, address):
    """
    Filter both DUTXOs and UTXOs
    and create list of readable TXOs dict
    :param txos: list of outputs
    :param address: required address(bytes)
    :return: list of TXOs dict
    """

    txos = []
    for tx in txos:
        for output_no in txos[tx]:
            if txos[tx][output_no].receiver == address:
                txos.append({
                    "tx": tx,
                    "hex": rlp_serializer.encode(
                        txos[tx][output_no]).hex(),
                    "output_no": output_no,
                    "value": txos[tx][output_no].value
                })
    # TODO remove
    if not txos:
        txos = [
            {
                "tx": b'Tests'.hex(),
                "hex": b'TEST'.hex(),
                "output_no": 69,
                "value": 1000
            }
        ]

    return txos


@dispatcher.add_method
def get_utxos(address):
    """
    Return UTXOs of given address
    :param address: address(hex)
    :return: list of UTXOs dict
    """
    logger.info("Getting UTXOs of: %s", address)
    utxos = state.get_utxos()
    return filter_txos(utxos, bytes.fromhex(address))


@dispatcher.add_method
def get_dutxos(address):
    """
    Return DUTXOs of given address
    :param address: address(hex)
    :return: list of DUTXOs dict
    """
    logger.info("Getting DUTXOs of: %s", address)
    dutxos = state.get_dutxos()
    return filter_txos(dutxos, bytes.fromhex(address))


@dispatcher.add_method
def get_current_offers(token_in, token_out):
    """
    Return all current offers
    :param token_in: Filter on token being sold
    :param token_out: Filter on expected payment token
    :return: list of json serialized offers
    """
    logger.info("Getting current offers")
    offers = state.get_active_offers()
    offers = list(filter(lambda o:
                         token_in in (ALL, o.token_in) and
                         token_out in (ALL, o.token_out),
                         offers))

    serialized_offers = list(map(lambda offer: json_serializer.encode(offer),
                                 offers))
    return serialized_offers


@dispatcher.add_method
def get_tx(tx_hash):
    """
    Get transaction from blockchain
    :param tx_hash: hash of the transaction
    :return: Transaction / None if tx does not exist
    """

    try:
        transaction = state.get_transaction(bytes.fromhex(tx_hash))
    except ValueError:
        logger.info("Transaction not found, hex: %s", tx_hash)
        return None
    return json_serializer.encode(transaction.transaction)


@dispatcher.add_method
def publish_transaction(signed_tx_json):
    """
    Add SignedTransaction to the blockchain
    :param signed_tx_json: serialized SignedTransaction
    :return: True if transaction is added
    """
    signed_tx = json_serializer.decode(signed_tx_json)
    print("{}: {}".format(type(signed_tx).__name__,
                          json_serializer.encode(signed_tx)))

    try:
        state.add_pending_tx(signed_tx)
    except Full:
        logger.exception("Cannot add transaction")
        return False

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
