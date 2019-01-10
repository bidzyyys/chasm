import configparser
import os

CONFIG_FILE = os.path.join(os.getcwd(), "config.ini")


def get_config(file_file=CONFIG_FILE):
    parser = configparser.ConfigParser()
    parser.read(os.path.abspath(os.path.expanduser(file_file)))
    return parser
