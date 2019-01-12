import configparser
import os


def _canonize_path(path):
    return os.path.abspath(os.path.expanduser(path))


def default_config_dir():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_dir = os.path.join(dir_path, "../../config")
    return _canonize_path(config_dir)


def default_config_file():
    return os.path.join(default_config_dir(), 'config.ini')


def default_test_config_file():
    return os.path.join(default_config_dir(), 'dev.ini')


DEFAULT_CONFIG_DIR = default_config_dir()
DEFAULT_CONFIG_FILE = default_config_file()
DEFAULT_TEST_CONFIG = default_test_config_file()


class Config:

    def __init__(self, config_files=DEFAULT_CONFIG_FILE):
        self.parser = configparser.ConfigParser()
        if not isinstance(config_files, list):
            config_files = [config_files]
        assert config_files == self.parser.read(config_files)

    def logger_level(self):
        return self.parser.get('LOGGER', 'level')

    def cli_node(self):
        return self.parser.get('CLI', 'node')

    def rpc_port(self):
        return self.parser.getint('RPC', 'port')

    def block_interval(self):
        return self.parser.getint('XPEER', 'block_interval')

    def pending_txs(self):
        return self.parser.getint('XPEER', 'pending_txs')

    def miner(self):
        str_addr = self.parser.get('XPEER', 'miner_address')
        return bytes.fromhex(str_addr[2::])

    def data_dir(self):
        return _canonize_path(self.parser.get('DEFAULT', 'data_dir'))

    def mining_workers(self):
        return self.parser.getint('XPEER', 'miner_threads')
