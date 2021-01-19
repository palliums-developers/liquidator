import time
import json
import os
from violas_client import Client as ViolasClient
from http_client import Client as HttpClient

class Client:
    REQUEST_INTERVAL = 60*60
    _last_currency_ids = {}

    def __init__(self, chain_url, dd_addr, create_child_vasp_url):
        url = chain_url
        self._dd_addr = dd_addr
        self._client = ViolasClient.new(url)
        self._http_client = HttpClient(create_child_vasp_url)

    def mint_coin(self, account, currency_code, amount, currency_id=None):
        if self._client.get_account_state(account.address_hex) is None:
            self._http_client.try_create_child_vasp_account(account)

        id = self.get_currency_id(currency_code)
        if currency_id is not None and id is not None:
            print(currency_id, id)
            if currency_id <= id:
                print("mint_coin", currency_code, amount, currency_id)
                return

        # if not self.has_apply_request(currency_code):
        if currency_code not in self._client.get_account_registered_currencies(account.address_hex):
            self._client.add_currency_to_account(account, currency_code)
        if currency_id is not None:
            tran_id = f"{currency_code}_{currency_id}_{amount}"
        else:
            tran_id = f"{os.urandom(16).hex()}"
        data = {
            "flag":"violas",
            "type":"funds",
            "opttype":"map",
            "chain": "violas",
            "tran_id": tran_id,
            "token_id": currency_code,
            "amount": amount,
            "to_address": f"0x{account.address_hex}",
            "state":"start"
        }
        self._client.transfer_coin(account, self._dd_addr, 1, data=json.dumps(data), currency_code="VLS")
        self.set_currency_id(currency_code, currency_id)
        return True
        # return False


    @classmethod
    def get_currency_id(cls, currency_code):
        return cls._last_currency_ids.get(currency_code)

    @classmethod
    def set_currency_id(cls, currency_code, id):
        cls._last_currency_ids[currency_code] = id

