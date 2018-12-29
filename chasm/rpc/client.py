"""RPC Client"""

import json

import requests

from . import LOGGER


def run(host, port):
    url = "http://{}:{}/jsonrpc".format(host, port)
    headers = {'content-type': 'application/json'}

    # Example echo method
    payload = {
        "method": "echo",
        "params": ["echome!"],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(
        url, data=json.dumps(payload), headers=headers).json()

    assert response["result"] == "echome!"
    assert response["jsonrpc"]
    assert response["id"] == 0

    LOGGER.info("Response: " + str(response))
