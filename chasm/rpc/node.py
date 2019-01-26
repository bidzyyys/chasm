"""RPC Server"""
from queue import Full
from threading import Thread

from jsonrpc import Dispatcher, JSONRPCResponseManager
from rlp.exceptions import RLPException
from werkzeug import serving
from werkzeug.serving import ThreadedWSGIServer
from werkzeug.wrappers import Request, Response

from chasm.maintenance.config import Config
from chasm.maintenance.logger import Logger
from chasm.serialization.json_serializer import JSONSerializer
from chasm.serialization.rlp_serializer import RLPSerializer
from chasm.services_manager import Service
from chasm.state.state import State
from . import ALL, ALL_ADDRESSES

json_serializer = JSONSerializer()
rlp_serializer = RLPSerializer()


class RPCServer:

    def __init__(self, state):
        self._state = state
        self._logger = Logger('chasm.rpc.handler')

    @staticmethod
    def _filter_txos(txos, address):
        """
        Filter both DUTXOs and UTXOs
        and create list of readable TXOs dict
        :param txos: dictionary of outputs of outputs
        :param address: required address(bytes)
        :return: list of TXOs dict
        """

        result = []
        for (tx, output_no), txo in txos.items():
            if hasattr(txo, 'receiver') and txo.receiver == address:
                result.append({
                    "tx": tx.hex(),
                    "output_no": output_no,
                    "value": txo.value
                })

        return result

    def get_utxos(self, address):
        """
        Return UTXOs of given address
        :param address: address(hex)
        :return: list of UTXOs dict
        """
        self._logger.info("Getting UTXOs of: %s", address)
        utxos = self._state.get_utxos()
        return self._filter_txos(utxos, bytes.fromhex(address))

    def get_exchange(self, exchange):
        """
        Get exchange
        :param exchange: exchange id
        :raise ValueError if exchange does not exist
        :return: tuple [OfferTransaction, MatchTransaction]
        """
        exchanges = self._state.get_matched_offers()
        for pair in exchanges:
            if pair[0] == exchange:
                offer = self._state.get_transaction(pair[0]).transaction
                match = self._state.get_transaction(pair[1]).transaction
                return offer, match
        raise ValueError("Exchange: {} does not exist".format(exchange))

    def get_confirmation_utxos(self, exchange):
        """
        Return UTXOs of given exchange
        :param exchange: exchange
        :return: list of UTXOs dict
        """
        self._logger.info("Getting UTXOs of exchange: %s", exchange)
        utxos = self._state.get_utxos()
        try:
            offer, match = self.get_exchange(exchange)
        except ValueError:
            self._logger.exception("Exchange does not exist!")
            return []

        return [
            {
                "tx": offer.hash().hex(),
                "output_no": offer.confirmation_fee_index,
                "value": utxos.get((offer.hash(),
                                    offer.confirmation_fee_index)).value
            },
            {
                "tx": match.hash().hex(),
                "output_no": match.confirmation_fee_index,
                "value": utxos.get((match.hash(),
                                    match.confirmation_fee_index)).value
            }
        ]

    def get_dutxos(self, address):
        """
        Return DUTXOs of given address
        :param address: address(hex)
        :return: list of DUTXOs dict
        """
        self._logger.info("Getting DUTXOs of: %s", address)
        dutxos = self._state.get_dutxos()
        return self._filter_txos(dutxos, bytes.fromhex(address))

    def get_current_offers(self, token_in, token_out):
        """
        Return all current offers
        :param token_in: Filter on token being sold
        :param token_out: Filter on expected payment token
        :return: list of json serialized offers
        """
        self._logger.info("Getting current offers")
        offers = self._state.get_active_offers()
        offers = list(filter(lambda o:
                             token_in in (ALL, o.token_in) and
                             token_out in (ALL, o.token_out),
                             offers.values()))

        serialized_offers = list(map(lambda offer: json_serializer.encode(offer),
                                     offers))
        return serialized_offers

    def get_tx(self, tx_hash):
        """
        Get transaction from blockchain
        :param tx_hash: hash of the transaction
        :return: Transaction / None if tx does not exist
        """
        try:
            transaction = self._state.get_transaction(bytes.fromhex(tx_hash))
        except (ValueError, KeyError):
            self._logger.info("Transaction not found, hex: %s", tx_hash)
            return None
        return json_serializer.encode(transaction.transaction)

    def publish_transaction(self, signed_tx_json):
        """
        Add SignedTransaction to the blockchain
        :param signed_tx_json: serialized SignedTransaction
        :return: True if transaction is added
        """

        self._logger.info("Publishing tx: %s",
                          json_serializer.encode(signed_tx_json))

        result = True
        try:
            signed_tx = json_serializer.decode(signed_tx_json)
            self._state.add_pending_tx(signed_tx)
        except RLPException:
            self._logger.exception("Cannot deserialize transaction")
            result = False
        except Full:
            self._logger.exception("Cannot add transaction")
            result = False

        return result

    def get_matches(self, offer_addr, match_addr):
        """
        Get pairs of offer and its match filtered by addresses
        :param offer_addr: address to filter offers
        :param match_addr: address to filter matches
        :return: list of tuples (OfferTransaction, MatchTransaction)
        transactions are serialized into json
        """
        self._logger.info("Getting matches, offer_addr: %s, match_addr: %s",
                          offer_addr, match_addr)

        matches = self._state.get_matched_offers()

        result = []
        for match_pair in matches:
            try:
                offer = self._state.get_transaction(match_pair[0]).transaction
                match = self._state.get_transaction(match_pair[1]).transaction
                if offer_addr in (offer.address_out.hex(), ALL_ADDRESSES) and \
                        match_addr in (match.address_in.hex(), ALL_ADDRESSES):
                    result.append((json_serializer.encode(offer),
                                   json_serializer.encode(match)))
            except (ValueError, IndexError):
                self._logger.error("Got hash of unknown transaction")

        return result

    def hello(self):
        """
        Hello world method
        Check if server responds to request
        :return: elho(as SMTP)
        """
        return "elho"


class RPCServerService(Service):
    def __init__(self, state: State, config: Config):
        self._prototype = RPCServer(state)
        self._dispatcher = Dispatcher()
        self._logger = Logger('chasm.rpc.server')

        self._port = config.get('rpc_port')
        self._server_thread: Thread = None
        self._server: ThreadedWSGIServer = None

    def application(self, request: Request):
        """
        Node(server) application
        :param request:
        :return: None
        """

        self._logger.info('Got a request.')

        response = JSONRPCResponseManager.handle(
            request.data, self._dispatcher)
        return Response(response.json, mimetype='application/json')

    def start(self, stop_condition):
        self._dispatcher.build_method_map(self._prototype)

        application = Request.application(self.application)

        self._server = serving.make_server(host='localhost', port=self._port, app=application, threaded=True)
        self._server_thread = Thread(target=lambda: self._server.serve_forever())
        self._server_thread.start()

        return True

    def is_running(self):
        return self._server_thread.is_alive()

    def stop(self):
        self._server.shutdown()
        self._server_thread.join()
