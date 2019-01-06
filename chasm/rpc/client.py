"""RPC Client"""

import json
import os
import re
import time
from getpass import getpass

import requests
from Crypto.Cipher import AES
from ecdsa import SigningKey
from ecdsa.der import UnexpectedDER

from chasm.consensus import CURVE
from chasm.consensus.primitives.transaction import Transaction, \
    OfferTransaction, MatchTransaction, UnlockingDepositTransaction
from chasm.consensus.primitives.tx_input import TxInput
from chasm.consensus.primitives.tx_output import TransferOutput, \
    XpeerOutput, XpeerFeeOutput
from . import logger, IncorrectPassword, PWD_LEN, ENCODING, \
    KEYSTORE, KEY_FILE_REGEX, PAYLOAD_TAGS, METHOD, PARAMS, \
    RPCError, token_from_name, ALL_TOKENS, TIMEOUT_FORMAT


# pylint: disable=invalid-name

def get_password(prompt="Type password: "):
    """
    Get password from user input without echoing
    :param prompt: prompt for user
    :return: 16 characters password
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
    :return: JSON in string representation
    """
    with open(filename) as f:
        json_str = json.load(f)
        return json_str


def load_json_from_file(filename):
    """
    Loads json data from filename
    :param filename: file to be read
    :return: json data in dict object
    """
    filename = filename.replace("~", os.path.expanduser("~"))
    json_str = read_json_file(filename)
    return json.loads(json_str)


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
    :raise InvalidAccountFile: if account already exists
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

    save_json(json.dumps(account), filename)

    return filename


def generate_account(args, pwd=None):
    """
    Generates new account with encrypted private key
    Keys are stored in a file given by user
    When path does not exist, it gets created
    :param pwd:
    :param args: args given by user
    :raise RuntimeError: when any action goes wrong
    :return: None
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
    keyfile = save_account(priv_key, pub_key, password, args.datadir)
    pub_key_hex = pub_key.hex()

    logger.info("Account generated successfully!")
    print("Address: {}".format(pub_key_hex))
    print("File: {}".format(keyfile))


def get_address(keyfile):
    """
    Get address from given account file
    :param keyfile: file with account configuration
    :return: address(public key)
    """
    try:
        account_info = load_json_from_file(keyfile)
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
    :param node: node hostname
    :param port: node port
    :return: balance of each address (dict[address]=balance))
    """
    try:
        utxos = get_utxos(address[0], node, port)
    except RPCError:
        logger.exception("Cannot get UTXOs of: %s", address[0],
                         exc_info=False)
        raise RuntimeError("Cannot count balance!")

    balance = sum(utxo["value"] for utxo in utxos)
    return balance


def show_balance(args):
    """
    Display balance of the account
    :param args: args given by user
    :return: None
    """
    balance = count_balance(args.address, args.node, args.port)
    print("Balance: {} bdzys".format(balance))


def show_all_funds(args):
    """
    Display balance of all accounts from datadir
    :param args: args given by user
    :return: None
    """

    addresses = get_addresses(args.datadir)
    total_balance = 0.0
    for address in addresses:
        balance = count_balance(address, args.node, args.port)
        print("Balance: {} bdzys".format(balance))
        print("Address: {}\n".format(address[0]))
        total_balance += balance

    print("Total: {} bdzys".format(total_balance))


def get_utxos(address, host, port):
    """
    Get UTXOs of given address

    Calls remote method through json-rpc

    :param address: owner of UTXOs
    :param host: node hostname
    :param port: node port
    :return: list of UTXOs
    """
    payload = PAYLOAD_TAGS.copy()
    payload[METHOD] = "get_utxos"
    payload[PARAMS] = [address]

    utxos = run(host=host, port=port, payload=payload)

    return utxos


def get_current_offers(host, port):
    """
    Get all current offers

    Calls remote method through json-rpce
    :param host: node hostname
    :param port: node port
    :return: list of current offers
    """
    payload = PAYLOAD_TAGS.copy()
    payload[METHOD] = "get_current_offers"
    payload[PARAMS] = []
    try:
        offers = run(host=host, port=port, payload=payload)
    except RPCError:
        raise RuntimeError("Cannot get current offers")

    return offers


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

    offers = get_current_offers(args.node, args.port)
    offers = list(filter(lambda o:
                         token_in in (ALL_TOKENS, o.token_in) and
                         token_out in (ALL_TOKENS, o.token_out),
                         offers))
    print("Current offers: {}".format(len(offers)))
    for offer in offers:
        print("Hash: {}".format(offer.hash))
        print("Token: {}".format(offer.token_in))
        print("Amount: {}".format(offer.value_in))
        print("Expected token: {}".format(offer.token_out))
        print("Price: {}".format(offer.value_out))


def build_tx_from_json(tx_json):
    return []


def build_tx(args):
    """
    Build any transaction from json file

    Display it for user(in json and hex format)
    :param args: Args given by user
    :return: None
    """

    transaction = build_tx_from_json(args.filename)
    print(__name__ + str(args))


def show_account_history(args):
    print(__name__ + str(args))


def show_transaction(args):
    print(__name__ + str(args))


def get_priv_key(account):
    """
    Unlock decrypted key
    :param account: account configuration
    :raise RuntimeError: if get incorrect password
    (failed to build SigningKey from der representation
    :return: SigningKey
    """
    priv_key_der = decrypt_aes(password=get_password("Unlock private key: "),
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
        utxos = get_utxos(address=address, host=node, port=port)
    except RPCError:
        raise RuntimeError("Cannot get UTXOs of: {}".format(address))

    sorted_utxos = sorted(utxos, key=lambda utxo: utxo["value"])
    funds = 0.0
    for index, utxo in enumerate(sorted_utxos):
        funds += utxo["value"]
        if funds >= amount:
            return sorted_utxos[:index + 1], funds

    raise ValueError("Cannot collect required value")


def sign(data, datadir, address):
    """
    Sign transaction with private key matching given address
    :param data: binary data to be signed
    :param datadir: directory with keystore
    :param address: address (public key)
    :return: signed transaction(bytes)
    """

    try:
        account = get_account_data(datadir, address)
    except FileNotFoundError:
        raise RuntimeError("Cannot sign given data")

    priv_key = get_priv_key(account)

    return priv_key.sign(data)


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

    inputs = list(map(lambda utxo: TxInput(tx_hash=bytes.fromhex(utxo["tx_hash"]),
                                           output_no=int(utxo["output_no"])),
                      utxos))

    own_transfer = TransferOutput(value=int(collected_funds - amount), receiver=owner)

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
    reqested_transfer = TransferOutput(value=int(amount), receiver=receiver)

    return Transaction(inputs=inputs, outputs=[reqested_transfer, own_transfer])


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

    requested_transfer = build_transfer_tx(node=args.node,
                                           port=args.port,
                                           amount=args.value,
                                           receiver=args.receiver,
                                           owner=args.owner,
                                           tx_fee=args.fee)

    print(str(requested_transfer))
    logger.info("Transfer tx created")


def show_matchings(args):
    print(__name__ + str(args))


def show_offers(args):
    print(__name__ + str(args))


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
    deposit_output = TransferOutput(value=deposit, receiver=address)
    confirmation_output = XpeerFeeOutput(value=confirmation_fee)

    return OfferTransaction(inputs=inputs,
                            outputs=[deposit_output, confirmation_output, own_transfer],
                            token_in=int(token_in.value), value_in=int(value_in),
                            token_out=int(token_out.value), value_out=int(value_out),
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

    offer = build_offer(node=args.node, port=args.port, address=args.address,
                        token_in=token_in, value_in=args.amount,
                        token_out=token_out, value_out=args.price,
                        receive_address=args.receive,
                        confirmation_fee=args.confirmation, deposit=args.deposit,
                        timeout=timeout, tx_fee=args.fee)

    print(offer)

    logger.info("Offer created successfully")


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
    deposit_output = TransferOutput(value=deposit, receiver=address)
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
    match = build_match(node=args.node, port=args.port,
                        address=args.address, offer_hash=args.offer,
                        receive=args.receive, tx_fee=args.fee,
                        confirmation_fee=args.confirmation, deposit=args.deposit)

    print(match)

    logger.info("Match created successfully")


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

    inputs, own_transfer = build_inputs(node=node, port=port, owner=address,
                                        amount=tx_fee + deposit)
    deposit_output = TransferOutput(value=deposit, receiver=address)

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

    unlock = build_unlock(node=args.node, port=args.port,
                          address=args.address, offer_hash=args.offer,
                          deposit=args.deposit, tx_fee=args.fee,
                          side=args.side, proof=args.proof)

    print(unlock)

    logger.info("Unlock deposit transaction created successfully")


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
        account = load_json_from_file(file)
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
    reqested_transfer = XpeerOutput(value=int(amount), receiver=receiver,
                                    exchange=bytes.fromhex(offer_hash))

    return Transaction(inputs=inputs, outputs=[reqested_transfer, own_transfer])


def xpeer_transfer(args):
    """
    Transfer xpc as a part of an exchange
    :param args: args given by user
    :return: None
    """

    xpeer_transfer = build_xpeer_transfer(node=args.node,
                                          port=args.port,
                                          amount=args.value,
                                          receiver=args.receiver,
                                          owner=args.owner,
                                          tx_fee=args.fee,
                                          offer_hash=args.offer)

    print(xpeer_transfer)

    logger.info("xpeer transfer created successfully")
