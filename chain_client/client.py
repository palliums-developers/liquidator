import time
import json
import os
from violas_client import Client as ViolasClient
from http_client import Client as HttpClient

CHAIN_URL = "http://13.68.141.242:50001"
DD_ADDR = "00000000000000000042524746554e44"

class Client:
    REQUEST_INTERVAL = 60

    def __init__(self, chain_url=None, dd_addr=None):
        url = chain_url or CHAIN_URL
        self._dd_addr = dd_addr or DD_ADDR
        self._client = ViolasClient.new(url)
        self._apply_recodes = {}
        self._http_client = HttpClient()

    def mint_coin(self, account, currency_code, amount):
        if self._client.get_account_state(account.address_hex) is None:
            self._http_client.try_create_child_vasp_account(account)

        if not self.has_apply_request(currency_code):
            if currency_code not in self.get_registered_currencies(account.address_hex):
                self._client.add_currency_to_account(account, currency_code)
            data = {
                "flag":"violas",
                "type":"funds",
                "opttype":"map",
                "chain": "violas",
                "tran_id":f"{os.urandom(16).hex()}",
                "token_id": currency_code,
                "amount": amount,
                "to_address": f"0x{account.address_hex}",
                "state":"start"
            }
            self._client.transfer_coin(account, self._dd_addr, 1, data=json.dumps(data), currency_code="VLS")

    def get_balance(self, addr, currency_code):
        return self._client.get_balance(addr, currency_code)

    def transfer(self, sender_account, receiver_address, currency_code, amount):
        return self._client.transfer_coin(sender_account, receiver_address, amount, currency_code=currency_code)

    def get_registered_currencies(self, addr):
        return self._client.get_balances(addr).keys()

    def has_apply_request(self, currency_code):
        last_time = self._apply_recodes.get(currency_code)
        if last_time is None:
            return False
        cur_time = int(time.time())
        if cur_time - last_time > self.REQUEST_INTERVAL:
            self._apply_recodes.pop(currency_code)
            return False
        return True


