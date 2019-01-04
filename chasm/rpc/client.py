"""RPC Client"""

import json
import os
from getpass import getpass

import requests
from Crypto.Cipher import AES
from ecdsa import SigningKey

from chasm import consensus
from . import logger, IncorrectPassword, PWD_LEN, ENCODING, \
    InvalidAccountFile


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


# def read_priv_key():
#     priv_der = decrypt_aes(password, nonce=bytes.fromhex(account['nonce']),
#                            encrypted_data=bytes.fromhex(account['priv_key']))

def save_account(priv_key, pub_key, password, filename):
    """
    Save account properties into json file
    :param priv_key: private key
    :param pub_key: public key
    :param password: password to encrypt key
    :param filename: file to be saved
    :raise InvalidAccountFile: if account already exists
    :return: None
    """
    encrypted_priv_key, nonce = encrypt_aes(password, priv_key)

    account = {
        "address": pub_key.hex(),
        "priv_key": encrypted_priv_key.hex(),
        "nonce": nonce.hex()
    }

    filename = filename.replace("~", os.path.expanduser("~"))
    if os.path.isfile(filename):
        raise InvalidAccountFile("Account exists: %s" % filename)

    save_json(json.dumps(account), filename)


def generate_account(args, pwd=None):
    """
    Generates new account with encrypted private key
    Keys are stored in a file given by user
    When path does not exist, it gets created
    :param pwd:
    :param args: args given by user
    :raise RuntimeError: when any action goes wrong
    :return: address(public key) in hex string format
    """

    if pwd is None:
        try:
            password = create_password()
        except IncorrectPassword:
            logger.exception("Unexpected error while getting new password")
            raise RuntimeError("Failed to generate new account")
    else:
        password = pwd

    priv_key, pub_key = generate_keys()

    try:
        save_account(priv_key, pub_key, password, args.keyfile)
    except InvalidAccountFile:
        logger.exception("Account file already exists!")
        raise RuntimeError("Failed to generate new account")

    pub_key_hex = pub_key.hex()
    logger.info("Account generated successfully, address: %s" % pub_key_hex)
    return pub_key_hex


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
    """
    Show address from given account configuration file
    :param args: args given by user
    :return: address(public key) in hex string format
    """
    try:
        account_info = read_json(args.keyfile)
        pub_key_hex = account_info["address"]
        logger.info("Your address: %s" % pub_key_hex)
        return pub_key_hex
    except FileNotFoundError:
        logger.exception("Account does not exist!: %s" % args.keyfile)
        raise RuntimeError("Cannot get address from given file!")


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
