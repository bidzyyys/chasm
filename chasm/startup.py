import configparser
import os


def get_config(file_path):
    parser = configparser.ConfigParser()
    parser.read(os.path.abspath(os.path.expanduser(file_path)))
    return parser
