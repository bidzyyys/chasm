"""RPC Client"""

import datetime
import json
import os
import re
import time
from getpass import getpass

import requests
from Crypto.Cipher import AES
from ecdsa import SigningKey
from ecdsa.der import UnexpectedDER
from rlp.exceptions import RLPException

from chasm.consensus import CURVE
from chasm.consensus.primitives.transaction import Transaction, \
    OfferTransaction, MatchTransaction, UnlockingDepositTransaction, \
    SignedTransaction
from chasm.consensus.primitives.tx_input import TxInput
from chasm.consensus.primitives.tx_output import TransferOutput, \
    XpeerOutput, XpeerFeeOutput
from chasm.exceptions import IncorrectPassword, RPCError
from chasm.serialization.json_serializer import JSONSerializer
from chasm.serialization.rlp_serializer import RLPSerializer
from . import logger, PWD_LEN, ENCODING, Side, \
    KEYSTORE, KEY_FILE_REGEX, PAYLOAD_TAGS, METHOD, PARAMS, \
    token_from_name, TIMEOUT_FORMAT, get_token_name, \
    ALL_ADDRESSES

# pylint: disable=invalid-name

json_serializer = JSONSerializer()
rlp_serializer = RLPSerializer()


def get_password(prompt="Type password: "):
    """
    Get password from user input without echoing
    :param prompt: prompt for user
    :return: password
    """
    password = getpass(prompt=prompt)
    while len(password) < PWD_LEN:
        password = password + password

    return password[:PWD_LEN]


def create_password():
    """
    Creates password
    user must retype it
    :raise IncorrectPassword: when user types different passwords
    :return: password
    """
    pwd = get_password()
    if pwd != get_password("Retype password: "):
        raise IncorrectPassword("Incorrect password")
    else:
        return pwd


def create_path(dir_path):
    """
    Creates path is does not exist
    :param dir_path: path to create
    :return: None
    """

    os.makedirs(dir_path, exist_ok=True)


def save_json(data, filename):
    """
    Save json to given filename
    :param data: data in json format
    :param filename: file to be saved
    :return: None
    """
    filename = filename.replace("~", os.path.expanduser("~"))
    dir_path = os.path.dirname(filename)
    if dir_path != "":
        create_path(dir_path)
    with open(filename, 'w') as f:
        json.dump(data, f)


def read_json_file(filename):
    """
    Read json from given filename
    :param filename: path to file
    :return: json data in dict object
    """
    filename = filename.replace("~", os.path.expanduser("~"))
    with open(filename) as f:
        return json.load(f)


def read_data_file(filename):
    """
    Read data from given filename
    :param filename: path to file
    :return: data string
    """
    filename = filename.replace("~", os.path.expanduser("~"))
    with open(filename) as f:
        return f.read()


def generate_keys():
    """
    Generate new key pair
    :return: key pair in DER format
    """
    priv_key = SigningKey.generate(CURVE)
    pub_key = priv_key.get_verifying_key()

    return priv_key.to_der(), pub_key.to_der()


def create_aes_cipher(password, nonce=None):
    """
    Creates AES cipher
    :param password: key
    :param nonce: nonce
    :return: cipher, nonce
    """
    key = bytes(password, ENCODING)
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    nonce = cipher.nonce

    return cipher, nonce


def encrypt_aes(password, data):
    """
    AES data encryption
    :param password: key
    :param data: data to be encrypted
    :return: encrypted data and nonce(to create cipher)
    """
    cipher, nonce = create_aes_cipher(password)
    encrypted, _ = cipher.encrypt_and_digest(data)
    return encrypted, nonce


def decrypt_aes(password, nonce, encrypted_data):
    """
    AES data decryption
    :param password: key
    :param nonce: nonce
    :param encrypted_data: data to be decrypted
    :return: decrypted data
    """
    cipher, _ = create_aes_cipher(password, nonce)
    return cipher.decrypt(encrypted_data)


def save_account(priv_key, pub_key, password, datadir):
    """
    Save account properties into json file
    :param priv_key: private key
    :param pub_key: public key
    :param password: password to encrypt key
    :param datadir: current datadir
    :return: filename of the account data
    """
    encrypted_priv_key, nonce = encrypt_aes(password, priv_key)

    account = {
        "address": pub_key.hex(),
        "priv_key": encrypted_priv_key.hex(),
        "nonce": nonce.hex()
    }

    keyfile = "{}_{}.json".format(time.strftime("%Y%m%d_%H%M%S"),
                                  pub_key.hex()[-7:])
    filename = os.path.join(datadir, KEYSTORE, keyfile)

    save_json(account, filename)

    return filename


def generate_account(args):
    """
    Create new account
    :param args: args given by user
    :return: None
    """
    pub_key, keyfile = create_account(args.datadir)

    logger.info("Account generated successfully!")
    print("Address: {}".format(pub_key.hex()))
    print("File: {}".format(keyfile))


def create_account(datadir, pwd=None):
    """
    Generates new account with encrypted private key
    Keys are stored in a file given by user
    When path does not exist, it gets created
    :param datadir: datadir with keystore
    :param pwd: private key password
    :raise RuntimeError: when any action goes wrong
    :return: tuple(pub_key, keyfile)
    """
    if pwd is None:
        try:
            password = create_password()
        except IncorrectPassword:
            logger.exception("Unexpected error while getting new password",
                             exc_info=False)
            raise RuntimeError("Failed to generate new account")
    else:
        password = pwd

    priv_key, pub_key = generate_keys()
    keyfile = save_account(priv_key, pub_key, password, datadir)

    return pub_key, keyfile


def get_address(keyfile):
    """
    Get address from given account file
    :param keyfile: file with account configuration
    :return: address(public key)
    """
    try:
        account_info = read_json_file(keyfile)
        pub_key_hex = account_info["address"]
        return pub_key_hex
    except FileNotFoundError:
        logger.exception("Account does not exist!: %s", keyfile,
                         exc_info=False)
        raise RuntimeError("Cannot get address from given file!")


def find_account_files(datadir, filename_regex=KEY_FILE_REGEX):
    """
    Find all files with account data matching given regex
    :param datadir: directory to find for accounts
    :param filename_regex: regex for filenames
    :return: list of account files
    """
    datadir = datadir.replace("~", os.path.expanduser("~"))
    keystore = os.path.join(datadir, KEYSTORE)
    accounts = [os.path.join(keystore, f) \
                for f in os.listdir(os.path.join(datadir, KEYSTORE))
                if re.match(filename_regex, f)]

    return accounts


def get_addresses(datadir):
    """
    Get all addresses from given datadir
    :param datadir: datadir
    :return: list of tuples [address, keyfile]
    """
    accounts = find_account_files(datadir)

    addresses = [[get_address(f), f] for f in accounts]

    return addresses


def show_keys(args):
    """
    Display addresses from given datadir
    :param args: args given by user
    :return: None
    """

    addresses = get_addresses(args.datadir)

    for address in addresses:
        print("Keyfile: {}\nAddress: {}\n".format(address[1], address[0]))


def run(host, port, payload):
    """
    Send json-rpc request
    :param host: node hostname
    :param port: node port
    :param payload: request data
    :raise RPCError: if cannot establish connection or
    get a response with error
    :return: result of called method
    """
    url = "http://{}:{}/jsonrpc".format(host, port)
    headers = {'content-type': 'application/json'}

    try:
        response = requests.post(
            url, data=json.dumps(payload), headers=headers).json()
    except requests.exceptions.ConnectionError:
        raise RPCError("Cannot establish connection")

    if 'error' in response.keys():
        raise RPCError("Unexpected RPC error: {}".
                       format(response['error']['message']))

    return response['result']


def count_balance(address, node, port):
    """
    Count balance of an account
    :param address: owner of UTXOs
    :param node: node hostname
    :param port: node port
    :return: balance of each address (dict[address]=balance))
    """
    utxos = get_utxos(address=address, node=node, port=port)
    balance = sum(utxo["value"] for utxo in utxos)
    return balance


def get_utxos(address, node, port):
    """
    Get all UTXOs of the address
    :param address: owner of UTXOs
    :param node: node hostname
    :param port: node port
    :return: list of UTXOs
    """
    try:
        utxos = fetch_utxos(address, node, port)
    except RPCError:
        raise RuntimeError("Cannot get UTXOs of: {}".format(address))

    return utxos


def show_balance(args):
    """
    Display balance of the account
    :param args: args given by user
    :return: None
    """
    balance = count_balance(args.address, args.node, args.port)
    print("Balance: {} bdzys".format(balance))


def get_dutxos(address, node, port):
    """
    Get all DUTXOs of given address
    :param address: owner of DUTXOs
    :param node: node hostname
    :param port: node port
    :return: list of DUTXOs
    """
    try:
        dutxos = fetch_dutxos(address, node, port)
    except (RPCError, RuntimeError):
        raise RuntimeError("Cannot get DUTXOs of: {}".format(address))

    return dutxos


def show_dutxos(args):
    """
    Show all DUTXOs of the account
    :param args: args given by user
    :return: None
    """
    dutxos = get_dutxos(address=args.address, node=args.node,
                        port=args.port)
    balance = 0.0
    for dutxo in dutxos:
        display_txo(dutxo)
        balance += dutxo["value"]

    print("Total: {} bdzys".format(balance))


def show_utxos(args):
    """
    Show all UTXOs of the account
    :param args: args given by user
    :return: None
    """
    utxos = get_utxos(address=args.address, node=args.node,
                      port=args.port)
    balance = 0.0
    for utxo in utxos:
        display_txo(utxo)
        balance += utxo["value"]

    print("Total: {} bdzys".format(balance))


def show_all_funds(args):
    """
    Display balance of all accounts from datadir
    :param args: args given by user
    :return: None
    """

    addresses = get_addresses(args.datadir)
    total_balance = 0.0
    for address in addresses:
        balance = count_balance(address[0], args.node, args.port)
        print("Balance: {} bdzys".format(balance))
        print("Address: {}\n".format(address[0]))
        total_balance += balance

    print("Total: {} bdzys".format(total_balance))


def fetch_utxos(address, host, port):
    """
    Get UTXOs of given address

    Calls remote method through json-rpc

    :param address: owner of UTXOs
    :param host: node hostname
    :param port: node port
    :return: list of UTXOs dict
    """
    payload = PAYLOAD_TAGS.copy()
    payload[METHOD] = "get_utxos"
    payload[PARAMS] = [address]

    utxos = run(host=host, port=port, payload=payload)

    return utxos


def fetch_dutxos(address, host, port):
    """
    Get DUTXOs of given address

    Calls remote method through json-rpc

    :param address: owner of DUTXOs
    :param host: node hostname
    :param port: node port
    :return: list of DUTXOs dict
    """
    payload = PAYLOAD_TAGS.copy()
    payload[METHOD] = "get_dutxos"
    payload[PARAMS] = [address]

    dutxos = run(host=host, port=port, payload=payload)

    return dutxos


def display_txo(txo):
    """
    Display given txo
    :param txo: UTXO/DUTXO to be displayed
    :return: None
    """
    print("Hex: {}".format(txo["hex"]))
    print("Value: {} bdzys".format(txo["value"]))
    print("Output number: {}".format(txo["output_no"]))
    print("Transaction(hex): {}\n".format(txo["tx"]))


def fetch_current_offers(host, port, token_in, token_out):
    """
    Get all current offers

    Calls remote method through json-rpce
    :param host: node hostname
    :param port: node port
    :param token_in: Filter on token being sold
    :param token_out: Filter on expected payment token
    :raise RuntimeError: if an error occurs
    :return: list of current offers
    """
    payload = PAYLOAD_TAGS.copy()
    payload[METHOD] = "get_current_offers"
    payload[PARAMS] = [token_in, token_out]
    try:
        offers_json = run(host=host, port=port, payload=payload)
    except RPCError:
        raise RuntimeError("Cannot get current offers")

    try:
        offers = list(map(lambda offer: json_serializer.decode(offer),
                          offers_json))
    except RLPException:
        raise RuntimeError("Cannot deserialize offers")

    return offers


def display_offer(offer: OfferTransaction):
    """
    Display offer info
    :param offer: offer to be displayed
    :return: None
    """
    print("Hash: {}".format(rlp_serializer.encode(offer).hex()))
    print("Token: {}".format(get_token_name(offer.token_in)))
    print("Amount: {}".format(offer.value_in))
    print("Expected token: {}".format(get_token_name(offer.token_out)))
    print("Price: {}".format(offer.value_out))
    print("Timeout: {}".format(datetime.datetime.fromtimestamp(offer.timeout)))
    print("Payment address: {}\n".format(offer.address_out.hex()))


def display_match(match: MatchTransaction):
    """
    Display match info
    :param match: match to be displayed
    :return: None
    """
    print("Hash: {}".format(rlp_serializer.encode(match).hex()))
    print("Address: {}".format(match.address_in))


def show_marketplace(args):
    """
    Display all current offers
    :param args: args given by user
    :return: None
    """
    try:
        token_in = token_from_name(args.token)
        token_out = token_from_name(args.expected)
    except ValueError:
        raise RuntimeError("Cannot display current offers, invalid token")

    offers = fetch_current_offers(args.node, args.port,
                                  token_in,
                                  token_out)

    print("Current offers: {}".format(len(offers)))
    for offer in offers:
        display_offer(offer)


def build_tx_from_json(filename):
    """
    Deserialize transaction from json file
    :param filename: path to file
    :return: deserialized transaction
    """

    try:
        tx_json = read_data_file(filename)
        transaction = json_serializer.decode(tx_json)
    except (RLPException, FileNotFoundError, KeyError):
        raise RuntimeError("Cannot build transaction from file")

    return transaction


def build_tx(args):
    """
    Build any transaction from json file

    Display it for user(in json and hex format)
    :param args: Args given by user
    :return: None
    """

    transaction = build_tx_from_json(args.file)
    print("\n{}: {}".format(type(transaction).__name__,
                            str(json_serializer.encode(transaction))))
    print("\nHex: {}".format(rlp_serializer.encode(transaction).hex()))


def get_transaction(node, port, transaction):
    """
    Get transaction
    :param node: node hostname
    :param port: node port
    :param transaction: hash of the transaction(hex)
    :raise ValueError: if given transaction does not exist
    :raise RuntimeError: if rpc error occurs
    :return: transaction
    """
    payload = PAYLOAD_TAGS.copy()
    payload[METHOD] = "get_tx"
    payload[PARAMS] = [transaction]

    try:
        tx_json = run(host=node, port=port, payload=payload)
        if tx_json is None:
            raise ValueError("Given transaction does not exist!")

        tx = json_serializer.decode(tx_json)
    except (RPCError, RLPException):
        raise RuntimeError("Cannot get transaction from node!")

    return tx


def show_transaction(args):
    """
    Show transaction to the user
    :param args: args given by user
    :return: None
    """
    try:
        transaction = get_transaction(node=args.node, port=args.port,
                                      transaction=args.tx)
        display_transaction(transaction)
    except ValueError:
        print("Transaction does not exist!")


def get_priv_key(account, pwd=None):
    """
    Unlock decrypted key
    :param pwd: password to private key
    :param account: account configuration
    :raise RuntimeError: if get incorrect password
    (failed to build SigningKey from der representation
    :return: SigningKey
    """
    if pwd is None:
        password = get_password("Unlock private key: ")
    else:
        password = pwd

    priv_key_der = decrypt_aes(password=password,
                               encrypted_data=bytes.fromhex(account['priv_key']),
                               nonce=bytes.fromhex(account['nonce']))

    try:
        signing_key = SigningKey.from_der(priv_key_der)
    except UnexpectedDER:
        raise RuntimeError("Cannot unlock private key!")

    return signing_key


def get_utxos_for_tx(node, port, address, amount):
    """
    Get UTXOs that cover required amount
    :param node: node hostname
    :param port: node port
    :param address: address of the owner
    :param amount: amount to be covered
    :raise ValueError: if owner has too little money
    :raise RuntimeError: if an error occurs while getting UTXOs
    :return: UTXOs to be used in a transaction and their amount
    """
    try:
        utxos = fetch_utxos(address=address, host=node, port=port)
    except RPCError:
        raise RuntimeError("Cannot get UTXOs of: {}".format(address))

    sorted_utxos = sorted(utxos, key=lambda utxo: utxo["value"])
    funds = 0.0
    for index, utxo in enumerate(sorted_utxos):
        funds += utxo["value"]
        if funds >= amount:
            return sorted_utxos[:index + 1], funds

    raise ValueError("Cannot collect required value")


def sign_transaction(transaction, pub_key, datadir, priv_key=None):
    """
    Sign transaction with private key matching given address
    :param priv_key: Private key to sign transaction(for tests,
    default None)
    :param transaction: transaction to be signed
    :param datadir: directory with keystore
    :param pub_key: address (public key)
    :return: signed transaction(bytes)
    """

    if priv_key is None:
        try:
            account = get_account_data(datadir, pub_key)
        except FileNotFoundError:
            raise RuntimeError("Cannot get private key!")

        priv_key = get_priv_key(account)

    return transaction.sign(priv_key.to_string())


def sign_tx(tx_hex, pub_key, datadir, signing_key=None):
    """
    Build transaction from hash, then sign it
    :param tx_hex: transaction
    :param pub_key: public key(to find private key)
    :param datadir: datadir with private key
    :param signing_key: signing key - pass only in tests
    :return: signature or None
    """
    signature = None
    try:
        transaction = rlp_serializer.decode(bytes.fromhex(tx_hex))
        if get_acceptance_from_user(transaction, question="Sign transaction?"):
            signature = sign_transaction(transaction=transaction,
                                         pub_key=pub_key,
                                         datadir=datadir,
                                         priv_key=signing_key)
    except (RLPException, RuntimeError):
        raise RuntimeError("Cannot sign transaction!")

    return signature


def sign(args):
    """
    Sign transaction given by user(in hex format)
    :param args: args given by user
    :return: None
    """

    signature = sign_tx(tx_hex=args.tx, pub_key=args.address,
                        datadir=args.datadir)

    if signature is not None:
        print("\nSignature: {}".format(signature.hex()))


def build_inputs(node, port, amount, owner):
    """
    Build transaction inputs
    :param node: node hostname
    :param port: node port
    :param amount: amount to be covered
    :param owner: owner of UTXOs
    :raise RuntimeError: if cannot build inputs
    :return: list of inputs(TxInput) and own transfer(TransferOutput)
    """
    try:
        utxos, collected_funds = get_utxos_for_tx(node=node, port=port,
                                                  address=owner, amount=amount)
    except (ValueError, RuntimeError):
        raise RuntimeError("Cannot build inputs")

    inputs = list(map(lambda utxo: TxInput(tx_hash=bytes.fromhex(utxo["tx"]),
                                           output_no=int(utxo["output_no"])),
                      utxos))

    own_transfer = TransferOutput(value=int(collected_funds - amount),
                                  receiver=bytes.fromhex(owner))

    return inputs, own_transfer


# pylint: disable=too-many-arguments
def build_transfer_tx(node, port, amount, receiver, tx_fee, owner):
    """
    Build simple transfer transaction
    :param port: node port
    :param node: node hostname
    :param amount: value to be transferred
    :param receiver: receiver address
    :param tx_fee: transaction fee
    :param owner: owner address
    :return: Transaction
    """

    inputs, own_transfer = build_inputs(node=node, port=port,
                                        amount=amount + tx_fee, owner=owner)
    reqested_transfer = TransferOutput(value=int(amount),
                                       receiver=bytes.fromhex(receiver))

    return Transaction(inputs=inputs, outputs=[reqested_transfer, own_transfer])


def do_simple_transfer(node, port, amount, receiver, sender, tx_fee, datadir, signing_key=None):
    """
    Create transfer and then publish
    :param node: node hostname
    :param port: node port
    :param amount: amount to be transferred
    :param receiver: receiver address
    :param sender: sender address
    :param tx_fee: transaction fee
    :param datadir: datadir with sender keystore
    :param signing_key: sender's private key(for tests)
    :return: True if transaction is published
    """

    tx = build_transfer_tx(node=node,
                           port=port,
                           amount=amount,
                           receiver=receiver,
                           owner=sender,
                           tx_fee=tx_fee)

    logger.info("Transaction created successfully!")
    return publish_transaction(node, port, tx,
                               sender, datadir, signing_key)


def transfer(args):
    """
    Transfer given amount of xpc to the receiver
    with specified transaction fee

    Gets all UTXOs of given owner, then chooses the smallest
    to collect required value, difference between collected amount
    and required is sent back to the owner
    :param args: args given by user
    :return: None
    """

    if do_simple_transfer(node=args.node, port=args.port, amount=args.value,
                          receiver=args.receiver, sender=args.owner,
                          tx_fee=args.fee, datadir=args.datadir):
        logger.info("Transaction sent successfully!")


def show_matches(args):
    """
    Show all matches with given income address
    :param args: args given by user
    :return: None
    """

    match_pairs = fetch_matches(host=args.node, port=args.port,
                                offer_addr=ALL_ADDRESSES,
                                match_addr=args.address)

    print("Found matches: {}".format(len(match_pairs)))
    for pair in match_pairs:
        print("Match:")
        display_match(pair[1])
        print("Offer: {}"
              .format(rlp_serializer.encode(pair[0])
                      .hex()))


def show_accepted_offers(args):
    """
    Display all accepted offers with given income address
    :param args: args given by user
    :return: None
    """
    match_pairs = fetch_matches(host=args.node, port=args.port,
                                offer_addr=args.address,
                                match_addr=ALL_ADDRESSES)

    print("Found offers: {}".format(len(match_pairs)))
    for pair in match_pairs:
        print("Offer:")
        display_offer(pair[0])
        print("Match: {}"
              .format(rlp_serializer.encode(pair[1])
                      .hex()))


def fetch_matches(host, port, offer_addr, match_addr):
    """
    Fetch matches
    :param host: node hostname
    :param port: node port
    :param offer_addr: offer side income address(filter)
    :param match_addr: match side income address(filter)
    :return: list of tuples(OfferTransaction, MatchTransaction)
    """
    payload = PAYLOAD_TAGS.copy()
    payload[METHOD] = "get_matches"
    payload[PARAMS] = [offer_addr, match_addr]
    try:
        matches_json = run(host=host, port=port, payload=payload)
    except RPCError:
        raise RuntimeError("Cannot get matches")

    try:
        matches = list(map(lambda match: (json_serializer.decode(match[0]),
                                          json_serializer.decode(match[1])),
                           matches_json))
    except RLPException:
        raise RuntimeError("Cannot deserialize matches")

    return matches


# pylint: disable=too-many-locals
def build_offer(node, port, address, token_in, token_out, value_in, value_out,
                receive_address, confirmation_fee, deposit, timeout, tx_fee):
    """
    Create offer
    :param node: node hostname
    :param port: node port
    :param address: offer creator address
    :param token_in: token to be sold
    :param token_out: token to be accepted as a payment
    :param value_in: amount of sold tokens
    :param value_out: price of sold tokens
    :param receive_address: address for income
    :param confirmation_fee: fee for confirmation transaction
    :param deposit: deposit
    :param timeout: offer timeout(timestamp)
    :param tx_fee: transaction fee
    :return: OfferTransaction
    """

    inputs, own_transfer = build_inputs(node=node, port=port, owner=address,
                                        amount=tx_fee + confirmation_fee + deposit)
    deposit_output = TransferOutput(value=deposit, receiver=bytes.fromhex(address))
    confirmation_output = XpeerFeeOutput(value=confirmation_fee)

    return OfferTransaction(inputs=inputs,
                            outputs=[deposit_output, confirmation_output, own_transfer],
                            token_in=int(token_in), value_in=int(value_in),
                            token_out=int(token_out), value_out=int(value_out),
                            address_out=bytes.fromhex(receive_address),
                            deposit_index=int(0), confirmation_fee_index=int(1),
                            timeout=int(timeout))


def create_offer(args):
    """
    Create an exchange offer
    :param args: args given by user
    :return: None
    """
    try:
        timeout = time.mktime(time.strptime(args.timeout, TIMEOUT_FORMAT))
    except ValueError:
        raise RuntimeError("Invalid timeout format!")
    try:
        token_in = token_from_name(args.token)
        token_out = token_from_name(args.expected)
    except ValueError:
        raise RuntimeError("Invalid token given")

    tx = build_offer(node=args.node, port=args.port, address=args.address,
                     token_in=token_in, value_in=args.amount,
                     token_out=token_out, value_out=args.price,
                     receive_address=args.receive,
                     confirmation_fee=args.confirmation, deposit=args.deposit,
                     timeout=timeout, tx_fee=args.fee)

    logger.info("OfferTransaction created successfully!")
    if publish_transaction(args.node, args.port, tx,
                           args.address, args.datadir):
        logger.info("Transaction sent successfully!")


def build_match(node, port, address, offer_hash, receive, confirmation_fee, deposit, tx_fee):
    """
    Build match transaction
    :param tx_fee: transaction fee
    :param deposit: deposit fee
    :param confirmation_fee: confirmation fee
    :param receive: receive payment address
    :param offer_hash: offer hash
    :param node: node hostname
    :param port: node portname
    :param address: offer match creator
    :return: MatchTransaction
    """
    inputs, own_transfer = build_inputs(node=node, port=port,
                                        owner=address,
                                        amount=tx_fee + confirmation_fee + deposit)
    deposit_output = TransferOutput(value=deposit, receiver=bytes.fromhex(address))
    confirmation_output = XpeerFeeOutput(value=confirmation_fee)

    return MatchTransaction(inputs=inputs,
                            outputs=[deposit_output, confirmation_output, own_transfer],
                            exchange=bytes.fromhex(offer_hash),
                            address_in=bytes.fromhex(receive),
                            confirmation_fee_index=int(0), deposit_index=int(1))


def accept_offer(args):
    """
    Accept offer
    :param args: args given by user
    :return: None
    """
    tx = build_match(node=args.node, port=args.port,
                     address=args.address, offer_hash=args.offer,
                     receive=args.receive, tx_fee=args.fee,
                     confirmation_fee=args.confirmation, deposit=args.deposit)

    logger.info("MatchTransaction created successfully!")
    if publish_transaction(args.node, args.port, tx,
                           args.address, args.datadir):
        logger.info("Transaction sent successfully!")


def build_unlock(node, port, address, offer_hash, deposit, tx_fee, side, proof):
    """
    Build unlock deposit transaction
    :param node: node hostname
    :param port: node port
    :param address: requestor address
    :param offer_hash: offer hash
    :param deposit: deposit fee
    :param tx_fee: transaction fee
    :param side: side of the exchange
    :param proof: proof of honesty
    :return: UnlockDepositTransaction
    """

    if side not in [Side.OFFER_MAKER.value, Side.OFFER_TAKER.value]:
        raise RuntimeError("Unknown exchange side: {}".format(side))

    inputs, own_transfer = build_inputs(node=node, port=port, owner=address,
                                        amount=tx_fee + deposit)
    deposit_output = TransferOutput(value=deposit, receiver=bytes.fromhex(address))

    return UnlockingDepositTransaction(inputs=inputs,
                                       outputs=[deposit_output, own_transfer],
                                       exchange=bytes.fromhex(offer_hash),
                                       proof_side=int(side),
                                       tx_proof=bytes.fromhex(proof),
                                       deposit_index=int(0))


def unlock_deposit(args):
    """
    Unlock deposit
    :param args: args given by user
    :return: None
    """

    tx = build_unlock(node=args.node, port=args.port,
                      address=args.address, offer_hash=args.offer,
                      deposit=args.deposit, tx_fee=args.fee,
                      side=args.side, proof=args.proof)

    logger.info("UnlockingDepositTransaction created successfully!")
    if publish_transaction(args.node, args.port, tx,
                           args.address, args.datadir):
        logger.info("Transaction sent successfully!")


def get_account_data(datadir, pub_key_hex):
    """
    Find an return account data
    :param datadir: directory to look for keyfile
    :param pub_key_hex: hex of public key
    :raise FileNotFoundError: if cannot find account file
    :return: account configuration
    """
    filename_regex = r'[0-9]{8}_[0-9]{6}_%s.json' % pub_key_hex[-7:]
    account_files = find_account_files(datadir, filename_regex)
    for file in account_files:
        account = read_json_file(file)
        if account["address"] == pub_key_hex:
            return account
    raise FileNotFoundError("Cannot find account file for given address")


def build_xpeer_transfer(node, port, amount, receiver, tx_fee, owner, offer_hash):
    """
    Build transfer of xpc as a part of an exchange
    :param offer_hash: hash of the offer
    :param port: node port
    :param node: node hostname
    :param amount: value to be transferred
    :param receiver: receiver address
    :param tx_fee: transaction fee
    :param owner: owner address
    :return: Transaction
    """

    inputs, own_transfer = build_inputs(node=node, port=port,
                                        amount=amount + tx_fee, owner=owner)
    reqested_transfer = XpeerOutput(value=int(amount), receiver=bytes.fromhex(receiver),
                                    exchange=bytes.fromhex(offer_hash))

    return Transaction(inputs=inputs, outputs=[reqested_transfer, own_transfer])


def xpeer_transfer(args):
    """
    Transfer xpc as a part of an exchange
    :param args: args given by user
    :return: None
    """

    tx = build_xpeer_transfer(node=args.node,
                              port=args.port,
                              amount=args.value,
                              receiver=args.receiver,
                              owner=args.owner,
                              tx_fee=args.fee,
                              offer_hash=args.offer)

    logger.info("XpeerTransaction created successfully!")
    if publish_transaction(args.node, args.port, tx,
                           args.owner, args.datadir):
        logger.info("Transaction sent successfully!")


def publish_transaction(host, port, transaction, pub_key, datadir, signing_key=None):
    """
    Publish transaction
    Signs and send transaction
    :param signing_key: sender private key, only for tests
    :param host: node hostname
    :param port: node portname
    :param datadir: directory with keystore
    :param transaction: transaction to be published
    :param pub_key: sender public key
    :return: True if transaction was sent
    """
    result = get_acceptance_from_user(transaction)
    if result:
        signature = sign_transaction(transaction=transaction,
                                     pub_key=pub_key,
                                     datadir=datadir,
                                     priv_key=signing_key)

        result = send_transaction(host=host, port=port,
                                  transaction=transaction,
                                  signatures=[signature])

    return result


def display_transaction(transaction):
    """
    Display transaction to the user
    :param transaction: transaction to be displayed
    :return: None
    """

    try:
        print("\n{}: {}\n".format(type(transaction).__name__,
                                  json_serializer.encode(transaction)))
    except RLPException:
        print("Unknown type: {}".format(type(transaction).__name__))


def get_acceptance_from_user(transaction, question="Send transaction?"):
    """
    Show transaction to the user and get acceptance
    :param question: question to be displayed
    :param transaction: transaction to be signed
    :return: True if user accepts
    """
    display_transaction(transaction)
    cont = input("{} yes/no > ".format(question))
    while cont.lower() not in ("yes", "no"):
        cont = input("{} yes/no >".format(question))
    return cont.lower() == "yes"


def send_transaction(host, port, transaction, signatures):
    """
    Send transaction with its signatures
    :param host: node hostname
    :param port: node port
    :param transaction: transaction to be sent
    :param signatures: list of signatures
    :return: True if transaction was sent successfully
    """

    signed_transaction = SignedTransaction(transaction=transaction,
                                           signatures=signatures)

    payload = PAYLOAD_TAGS.copy()
    payload[METHOD] = "publish_transaction"
    payload[PARAMS] = [json_serializer.encode(signed_transaction)]

    return run(host=host, port=port, payload=payload)


def send_tx(node, port, tx_hex, signatures_hex):
    """
    Build transaction from hex and send with given signatures
    :param node: node hostname
    :param port: node port
    :param tx_hex: transaction(hex)
    :param signatures_hex: list of signatures(hex)
    :return: True if transaction was sent
    """
    result = False
    try:
        tx = rlp_serializer.decode(bytes.fromhex(tx_hex))
        signatures = list(map(lambda hex: bytes.fromhex(hex), signatures_hex))
    except (RLPException, ValueError):
        raise RuntimeError("Cannot send transaction")

    if get_acceptance_from_user(tx):
        result = send_transaction(host=node, port=port,
                                  transaction=tx, signatures=signatures)

    return result


def send(args):
    """
    Send transaction with its signatures
    :param args: args given by user
    :return: None
    """

    if send_tx(node=args.node, port=args.port,
               tx_hex=args.tx, signatures_hex=args.signatures):
        logger.info("Transaction sent successfully!")
