# pylint: disable=missing-docstring, too-many-arguments
import time

from chasm.consensus.primitives.transaction import Transaction, SignedTransaction
from chasm.consensus.primitives.tx_input import TxInput
from chasm.consensus.primitives.tx_output import TransferOutput
from chasm.maintenance.config import Config, DEFAULT_TEST_CONFIG
from chasm.maintenance.logger import Logger
from chasm.rpc import client

CONFIG = Config([DEFAULT_TEST_CONFIG])

Logger.level = CONFIG.get('logger_level')

client.logger = Logger('chasm.cli')


def sleep_for_block(secs=3):
    time.sleep(secs)


def mock_acceptance(s):
    return "yes"


def init_address(address, balance=0, utxos=0, dutxos_sum=0, dutxos=0):

    if utxos == 0:
        return

    miner_priv = b'\xad\xaf\xcd\xd4\x10\x18\x86~\\\xbd\xbb\x1e\xca\x9c\xa4\x0e\x00\x15v\xaa`0.jnO%\xae\xc9\x87(\xac'
    miner_pub = CONFIG.get('xpeer_miner_address')

    utxo = client.get_utxos(miner_pub.hex(), CONFIG.get('node'), CONFIG.get('rpc_port'))[0]
    inputs = [TxInput(bytes.fromhex(utxo['tx']), utxo['output_no'])]

    outputs = [TransferOutput(balance // utxos, bytes.fromhex(address)) for _ in range(utxos)]

    if (balance // utxos) * utxos != balance:
        outputs[0].value += balance - (balance // utxos) * utxos

    tx = Transaction(inputs, outputs)

    signatures = SignedTransaction.build_signed(tx, [miner_priv]).signatures

    client.send_transaction(CONFIG.get('node'), CONFIG.get('rpc_port'), tx, signatures)
    sleep_for_block()
