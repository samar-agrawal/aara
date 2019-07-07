'''
    List Contract events for given address
'''
import json
from functools import lru_cache

import requests
from flask import Flask, jsonify, render_template
from flask_apispec import use_kwargs
from marshmallow import fields

from websockets.exceptions import ConnectionClosed, InvalidStatusCode
from web3.exceptions import InfuraKeyNotFound

try:
    from web3.auto.infura import w3
except InfuraKeyNotFound:
    from web3.auto import w3

app = Flask(__name__)

@app.route("/public/hc", methods=['GET'])
def healthcheck():
    return "OK", 200

@app.errorhandler(AssertionError)
def handle_assertion(error):
    import traceback
    ret = {'code': 400, 'error': error.args[0], 'traceback': traceback.format_exc()}
    return jsonify(**ret), ret['code']

@app.route('/')
def home():
    return render_template('home.html')

@app.route("/api/data/", methods=['GET'])
@use_kwargs({
    'address': fields.String(required=True),
    'event_name': fields.String(required=True)
    })
def get_data(**kwargs):
    contract = ContractEventRead(**kwargs)

    try:
        assert contract.is_node_connected(), "Node not configured properly"
    except InvalidStatusCode:
        assert False, "Invalid Key"
    except ConnectionClosed:
        assert False, "Please retry"

    from_block = contract.get_from_block()
    data = contract.get_events(from_block=from_block)

    if not data:
        return '', 204

    return jsonify(data)

@lru_cache(maxsize=8)
def get_abi(address: str):
    '''
        To get a contract abi from etherscan and cache the result
        :address string: address in checksum format to get abi
        :rtype dict:
    '''

    #TODO: to find a better alternative
    abi_endpoint = 'https://api.etherscan.io/api?module=contract&action=getabi&address='

    response = requests.get(f'{abi_endpoint}{address}', timeout=20)
    response.raise_for_status()
    resp = response.json()
    assert resp['message'] == 'OK', resp['result']
    abi = json.loads(resp['result'])

    return abi

def get_formatted_data(event_list: list):
    '''
        Given a list of events, extract the relevant fields
        :params event_list: list of events
        :rtype generator: generator of dict event
    '''
    for event in event_list:
        event_dict = {k: event[k] for k in ('logIndex', 'blockNumber')}
        event_args = {k: event['args'][k] for k in ('owner', 'name', 'cost', 'expires')}
        event_dict.update(event_args)
        yield event_dict

class ContractEventRead:
    '''
        Constructs a contract class for fetching list of
        events for the event name in a contract
        :params address:
    '''

    def __init__(self, address: str, event_name: str, abi=None):
        self.address = address
        self.event_name = event_name
        self.abi = abi or get_abi(self.address)

        self._validate()
        if not w3.isChecksumAddress(self.address):
            self.address = w3.toChecksumAddress(self.address)

        self.contract = self.get_contract()

    def _validate(self):
        '''
            Check if the address defined is valid
            Check if the event name defined is valid
        '''
        assert w3.isAddress(self.address), "Invalid address format"
        assert self.event_name in self.get_events_from_abi(), f"Invalid Event {self.event_name}"

    def get_events_from_abi(self):
        '''
            Get a list of events defined within an ABI
            :rtype list:
        '''
        return [a['name'] for a in self.abi if a['type'] == 'event']

    @staticmethod
    def is_node_connected():
        '''
            Check if node (infura) is connected
        '''
        return w3.isConnected()

    @staticmethod
    @lru_cache(maxsize=8)
    def get_from_block(days: int = 1):
        '''
            Get block number based on number of days, assuming there are
            6500 transactions in a day, which might not be accurate
            This is cached based on number of days to prevent multiple calls.
            :params days: number of days to fetch data from
            :rtype int: block start by difference from latest block
        '''

        latest_block = w3.eth.blockNumber
        total_blocks = 65_00 * days #TODO: to find a better alternative
        return latest_block - total_blocks

    def get_contract(self):
        '''
            Get a contract object based on address and abi
            :rtype object: contract object
        '''
        return w3.eth.contract(address=self.address, abi=self.abi)

    def get_events(self, from_block: int):
        '''
            Get a list of events defined by range of block
            for the given event name.
            :params from_block: block to list data from
            :rtype list: return a list of dict of events
        '''
        self.get_contract()

        event_filter = self.contract.eventFilter(
            self.event_name, {'fromBlock':from_block, 'toBlock':'latest'})
        event_list = event_filter.get_all_entries()

        if not event_list:
            return []
        data = list(get_formatted_data(event_list))
        data.reverse()

        return data

    @staticmethod
    def to_eth(value:int):
        '''
            Convert currency from wei to ether
            :params int: value to convert from
        '''
        return w3.fromWei(value, 'ether')
