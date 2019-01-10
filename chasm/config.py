import configparser
import os


def _config_file():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_dir = os.path.join(dir_path, "../config")
    config_file = os.path.join(config_dir, 'config.ini')
    return _canonize_path(config_file)


def _canonize_path(path):
    return os.path.abspath(os.path.expanduser(path))


CONFIG_FILE = _config_file()


class Config:
    def __init__(self, config_files=CONFIG_FILE):
        self._parser = configparser.ConfigParser()
        self._parser.read(config_files)

    def logger_level(self):
        return self._parser.get('LOGGER', 'level')

    def cli_node(self):
        return self._parser.get('CLI', 'node')

    def rpc_port(self):
        return self._parser.getint('RPC', 'port')

    def block_interval(self):
        return self._parser.getint('XPEER', 'block_interval')

    def pending_txs(self):
        return self._parser.getint('XPEER', 'pending_txs')

    def miner(self):
        str_addr = self._parser.get('XPEER', 'miner_address')

        return bytes.fromhex(str_addr[2::])

    def data_dir(self):
        return _canonize_path(self._parser.get('DEFAULT', 'data_dir'))
