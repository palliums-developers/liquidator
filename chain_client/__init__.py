import time
import json
import os
from violas_client import Client as ViolasClient
from http_client import Client as HttpClient

class Client:
    REQUEST_INTERVAL = 60*60
    _apply_recodes = {}

    def __init__(self, chain_url, dd_addr, create_child_vasp_url):
        url = chain_url
        self._dd_addr = dd_addr
        self._client = ViolasClient.new(url)
        self._http_client = HttpClient(create_child_vasp_url)

    def mint_coin(self, account, currency_code, amount):
        if self._client.get_account_state(account.address_hex) is None:
            self._http_client.try_create_child_vasp_account(account)

        if not self.has_apply_request(currency_code):
            if currency_code not in self._client.get_account_registered_currencies(account.address_hex):
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
            self._apply_recodes[currency_code] = int(time.time())
            return True
        return False

    def has_apply_request(self, currency_code):
        last_time = self._apply_recodes.get(currency_code)
        if last_time is None:
            return False
        cur_time = int(time.time())
        if cur_time - last_time > self.REQUEST_INTERVAL:
            print(f"Specified time not mint {currency_code}, time: {last_time}")
            self._apply_recodes.pop(currency_code)
            return False
        return True



