import os
import sys
import json
import time
import dataclasses
from typing import Dict
from violas_client import Client as ViolasClient
from violas_client.lbrtypes.bytecode import CodeType
from network import DD_ADDR, CHAIN_URL, HTTP_SERVER, get_liquidator_account, create_database_manager
from http_client import Client as HttpClient
from network import DEFAULT_COIN_NAME
from bank.base import Base

@dataclasses.dataclass(init=False)
class CoinPorter(Base):
    _instance = None
    APPLY_VSL_INTERVAL = 60*60

    #上一次发币请求的id,初始值为0
    last_apply_ids: Dict[str, int]
    #上一次清算的id,初始值为aaply_id+1 清算时设置为last_apply_id+1
    last_liquidate_ids: Dict[str, int]
    #上一次申请vls的时间
    last_apply_vls_time: float
    #上一次清算的时间
    last_liquidate_times: Dict[str, float]

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "dd_addr"):
            self.dd_addr = DD_ADDR
            self.violas_client = ViolasClient.new(CHAIN_URL)
            self.http_client = HttpClient(HTTP_SERVER)
            self.liquidator_address = get_liquidator_account().address_hex

            self.last_apply_ids = dict()
            self.last_liquidate_ids = dict()
            self.last_apply_vls_time = 0
            self.last_liquidate_times = dict()

    def try_apply_coin(self, ac, currency_code, amount):
        if self.violas_client.get_account_state(ac.address) is None:
            self.http_client.try_create_child_vasp_account(ac)

        #申请vls会填写None
        if currency_code == DEFAULT_COIN_NAME:
            cur_time = time.time()
            if cur_time - self.last_apply_vls_time < self.APPLY_VSL_INTERVAL:
                return
            self.last_apply_vls_time = cur_time
            tran_id = f"{os.urandom(16).hex()}"
        else:
            apply_id = self.get_last_apply_id(currency_code)
            liquidate_id = self.get_last_liquidate_id(currency_code)
            #申请之后如果没有执行过清算， 则不再申请
            if liquidate_id <= apply_id:
                return
            tran_id = f"{currency_code}_{liquidate_id}_{amount}"
            self.set_last_apply_id(currency_code, liquidate_id)

        #添加币种支持
        if currency_code not in self.violas_client.get_account_registered_currencies(ac.address):
            self.violas_client.add_currency_to_account(ac, currency_code)

        data = {
            "flag":"violas",
            "type":"funds",
            "opttype":"liq",
            "chain": "violas",
            "tran_id": tran_id,
            "token_id": currency_code,
            "amount": amount,
            "to_address": f"0x{ac.address_hex}",
            "state":"start"
        }
        self.violas_client.transfer_coin(ac, self.dd_addr, 1, data=json.dumps(data), currency_code=DEFAULT_COIN_NAME)


    def add_tx(self, tx):
        if not tx.is_successful():
            return
        if tx.get_code_type() == CodeType.PEER_TO_PEER_WITH_METADATA:
            sender = tx.get_sender().lower()
            receiver = tx.get_receiver().lower()
            if sender.lower() == self.liquidator_address and receiver.lower() == self.dd_addr:
                data = tx.get_data()
                data = bytes.fromhex(data)
                try:
                    value = json.loads(bytes.decode(data))
                    currency, apply_id, amount = value.get("tran_id").split("_")
                    cur_id = self.get_last_apply_id(currency)
                    self.set_last_apply_id(currency, max(cur_id, int(apply_id)))
                except:
                    pass

    def update_from_db(self):
        db_manage = create_database_manager()
        self.last_apply_ids = db_manage.get("last_apply_ids", dict, {})
        self.last_liquidate_ids = db_manage.get("last_liquidate_ids", dict, {})
        self.last_apply_vls_time = db_manage.get("last_apply_vls_time", float, sys.maxsize)
        self.last_liquidate_times = db_manage.get("last_liquidate_times", dict, {})

    def update_to_db(self):
        db_manage = create_database_manager()
        db_manage.set("last_apply_ids", self.last_apply_ids)
        db_manage.set("last_liquidate_ids", self.last_liquidate_ids)
        db_manage.set("last_apply_vls_time", self.last_apply_vls_time)
        db_manage.set("last_liquidate_times", self.last_liquidate_times)

    def get_last_apply_id(self, currency_code):
        return self.last_apply_ids.get(currency_code, 0)

    def set_last_apply_id(self, currency_code, id):
        self.last_apply_ids[currency_code] = id

    def get_last_liquidate_id(self, currency_code):
        id = self.last_liquidate_ids.get(currency_code)
        if id is None:
            id = self.get_last_apply_id(currency_code)+1
            self.last_liquidate_ids[currency_code] = id
        return id


    def add_last_liquidate_id(self, currency_code):
        apply_id = self.get_last_apply_id(currency_code)
        liquidate_id = self.get_last_liquidate_id(currency_code)
        self.last_liquidate_ids[currency_code] = max(apply_id, liquidate_id) + 1

    def set_last_liquidate_time(self, currency_code):
        self.last_liquidate_times[currency_code] = time.time()

    def get_last_liquidate_time(self, currency_code):
        return self.last_liquidate_times.get(currency_code, sys.maxsize)

if __name__ == "__main__":
    porter = CoinPorter()
    ac = get_liquidator_account()
    porter.try_apply_coin(ac, "vBTC", 1000)
    print(porter.last_apply_ids)
    print(porter.last_liquidate_ids)