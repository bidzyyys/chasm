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

    def __init__(self, config_files, overridden={}):
        parser = configparser.ConfigParser()
        if not isinstance(config_files, list):
            config_files = [config_files]
        assert config_files == parser.read(config_files)

        self._configs = {**self._init(parser), **overridden}

    @staticmethod
    def _init(parser):
        return {'logger_level': parser.get('LOGGER', 'level'),
                'datadir': _canonize_path(parser.get('DEFAULT', 'data_dir')),
                'node': parser.get('CLI', 'node'),
                'rpc_port': parser.getint('RPC', 'port'),
                'xpeer_pending_txs': parser.getint('XPEER', 'pending_txs'),
                'xpeer_miner_address': bytes.fromhex(parser.get('XPEER', 'miner_address')),
                'xpeer_miner_threads': parser.getint('XPEER', 'miner_threads')}

    def get(self, param):
        return self._configs[param]
