"""RPC Server"""
from queue import Full

from jsonrpc import JSONRPCResponseManager, dispatcher
from rlp.exceptions import RLPException
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response

from chasm.serialization.json_serializer import JSONSerializer
from chasm.serialization.rlp_serializer import RLPSerializer
from . import logger, ALL, ALL_ADDRESSES

# pylint: disable=invalid-name

json_serializer = JSONSerializer()
rlp_serializer = RLPSerializer()


# state = State()


def filter_txos(txos, address):
    """
    Filter both DUTXOs and UTXOs
    and create list of readable TXOs dict
    :param txos: list of outputs
    :param address: required address(bytes)
    :return: list of TXOs dict
    """

    result = []
    for tx in txos:
        for output_no in txos[tx]:
            if txos[tx][output_no].receiver == address:
                result.append({
                    "tx": tx,
                    "hex": rlp_serializer.encode(
                        txos[tx][output_no]).hex(),
                    "output_no": output_no,
                    "value": txos[tx][output_no].value
                })

    return result


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

    logger.info("Publishing tx: %s",
                json_serializer.encode(signed_tx_json))

    result = True
    try:
        signed_tx = json_serializer.decode(signed_tx_json)
        state.add_pending_tx(signed_tx)
    except RLPException:
        logger.exception("Cannot deserialize transaction")
        result = False
    except Full:
        logger.exception("Cannot add transaction")
        result = False

    return result


@dispatcher.add_method
def get_matches(offer_addr, match_addr):
    """
    Get pairs of offer and its match filtered by addresses
    :param offer_addr: address to filter offers
    :param match_addr: address to filter matches
    :return: list of tuples (OfferTransaction, MatchTransaction)
    transactions are serialized into json
    """
    logger.info("Getting matches, offer_addr: %s, match_addr: %s",
                offer_addr, match_addr)

    matches = state.get_accepted_offers()

    result = []
    for match_pair in matches:
        try:
            offer = state.get_transaction(match_pair[0]).transaction
            match = state.get_transaction(match_pair[1]).transaction
            if offer_addr in (offer.address_out.hex(), ALL_ADDRESSES) and \
                    match_addr in (match.address_in.hex(), ALL_ADDRESSES):
                result.append((json_serializer.encode(offer),
                               json_serializer.encode(match)))
        except (ValueError, IndexError):
            logger.error("Got hash of unknown transaction")

    return result


@Request.application
def application(request):
    """
    Node(server) application
    :param request:
    :return: None
    """
    response = JSONRPCResponseManager.handle(
        request.data, dispatcher)
    return Response(response.json, mimetype='application/json')


def run(port, data_dir):
    """
    Run node application
    :param port: node port
    :param data_dir: path to database directory
    :return: None
    """
    run_simple("localhost", port, application)
    logger.info("Node application closed")
    state.close()
