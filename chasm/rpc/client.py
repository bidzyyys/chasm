"""RPC Client"""

import json
import os
import re
import time
from functools import reduce
from getpass import getpass

import requests
from Crypto.Cipher import AES
from ecdsa import SigningKey

from chasm import consensus
from . import logger, IncorrectPassword, PWD_LEN, ENCODING, \
    KEYSTORE, KEY_FILE_REGEX, PAYLOAD_TAGS, METHOD, PARAMS, \
    RPCError, BadResponse


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


def read_json(filename):
    """
    Read json data from filename
    :param filename: file to be read
    :return: data in json representation
    """
    filename = filename.replace("~", os.path.expanduser("~"))
    with open(filename) as f:
        json_str = json.load(f)
        return json.loads(json_str)


def generate_keys():
    """
    Generate new key pair
    :return: key pair in DER format
    """
    priv_key = SigningKey.generate(consensus.CURVE)
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
        account_info = read_json(keyfile)
        pub_key_hex = account_info["address"]
        return pub_key_hex
    except FileNotFoundError:
        logger.exception("Account does not exist!: %s", keyfile,
                         exc_info=False)
        raise RuntimeError("Cannot get address from given file!")


def get_addresses(datadir):
    """
    Get all addresses from given datadir
    :param datadir: datadir
    :return: list of tuples [address, keyfile]
    """
    datadir = datadir.replace("~", os.path.expanduser("~"))
    keystore = os.path.join(datadir, KEYSTORE)
    accounts = [os.path.join(keystore, f) \
                for f in os.listdir(os.path.join(datadir, KEYSTORE))
                if re.match(KEY_FILE_REGEX, f)]

    addresses = [[get_address(f), f] for f in accounts]

    return addresses


def receive(args):
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


def count_balance(datadir, node, port):
    """
    Count balance of an account
    :param datadir: datadir of an account
    :param node: node hostname
    :param port: node port
    :return: balance of each address (dict[address]=balance))
    """
    addresses = get_addresses(datadir)
    balance = {}
    for address in addresses:
        try:
            utxos = get_utxos(address[0], node, port)
        except RPCError:
            logger.exception("Cannot get UTXOs of: %s", address[0],
                             exc_info=False)
            raise RuntimeError("Cannot count balance!")
        funds = reduce((lambda utxo1, utxo2: utxo1.value + utxo2.value), utxos, 0.0)
        balance[address[0]] = funds

    return balance


def show_balance(args):
    """
    Display balance of the account
    :param args: args given by user
    :return: None
    """

    balance = count_balance(args.datadir, args.node, args.port)
    total_balance = 0.0
    for address in balance:
        print("Balance: {} xpc\nAddress: {}\n".format(balance[address], address))
        total_balance += balance[address]

    print("Total: {} xpc".format(total_balance))


def get_utxos(address, host, port):
    """
    Get UTXOs of given address

    Calls remote method through json-rpc

    :param address: owner of UTXOs
    :param host: node hostname
    :param port: node port
    :raise BadResponse: if any of UTXO has bad owner(address)
    :return: list of UTXOs
    """
    payload = PAYLOAD_TAGS.copy()
    payload[METHOD] = "get_utxos"
    payload[PARAMS] = [address]

    utxos = run(host=host, port=port, payload=payload)

    for utxo in utxos:
        if utxo.receiver != address:
            raise BadResponse("UTXO of different address")
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
    offers = get_current_offers(args.node, args.port)
    print("Current offers: {}".format(len(offers)))
    for offer in offers:
        print("Hash: {}".format(offer.hash))
        print("Token: {}".format(offer.token_in))
        print("Amount: {}".format(offer.value_in))
        print("Expected token: {}".format(offer.token_out))
        print("Price: {}".format(offer.value_out))


def show_account_history(args):
    print(__name__ + str(args))


def show_transaction(args):
    print(__name__ + str(args))


def transfer(args):
    print(__name__ + str(args))


def show_matchings(args):
    print(__name__ + str(args))


def show_offers(args):
    print(__name__ + str(args))


def create_offer(args):
    print(__name__ + str(args))


def accept_offer(args):
    print(__name__ + str(args))


def unlock_deposit(args):
    print(__name__ + str(args))

# def read_priv_key():
#     priv_der = decrypt_aes(password, nonce=bytes.fromhex(account['nonce']),
#                            encrypted_data=bytes.fromhex(account['priv_key']))
