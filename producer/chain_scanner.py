'''
    扫链服务
'''
import traceback
from queue import Queue
from threading import Thread
from violas_client import Client
from cache.api import liquidator_api
from conf.config import URL
from violas_client.lbrtypes.bytecode import CodeType
from db.account import AccountTable
from db.token import TokenTable
from db.height import HeightTable
from db.const import dsn
from cache.account import AccountView
from cache.token_info import TokenInfo


class ScannerThread(Thread):

    UPDATING = 0
    UPDATED = 1
    VERSION = 0

    def __init__(self, queue: Queue, config):
        global liquidator_api
        super(ScannerThread, self).__init__()
        self.client = Client.new(URL)
        self.queue = queue
        self.state = self.UPDATING
        if config.get("version") is not None:
            self.__class__.VERSION = config.get("version")
        self.last_version = self.__class__.VERSION
        self.account_table = AccountTable(dsn=dsn)
        self.token_table = TokenTable(dsn=dsn)
        self.height_table = HeightTable(dsn=dsn)

    @staticmethod
    def convert_accounts_from_cache_to_db(cache_accounts):
        accounts = []
        for account in cache_accounts.values():
            a = {
                "address": account.address,
                "lock_amounts": account.lock_amounts.amounts,
                "borrow_amounts": account.borrow_amounts.amounts,
                "health": account.health
            }
            accounts.append(a)
        return accounts

    @staticmethod
    def convert_accounts_from_db_to_cache(db_accounts):
        accounts = {}
        for account in db_accounts:
            a = AccountView(account[0], lock_amounts=account[1], borrow_amounts=account[2], health=account[3])
            accounts[account[0]] = a
        return accounts

    @staticmethod
    def convert_token_from_cache_to_db(cache_tokens):
        tokens = []
        for currency, token in cache_tokens.items():
            t = {
                "token": currency,
                "info": {
                    "total_supply": token.total_supply,
                    "total_reserves": token.total_reserves,
                    "total_borrows": token.total_borrows,
                    "borrow_index": token.borrow_index,
                    "oracle_price": token.oracle_price,
                    "price": token.price,
                    "collateral_factor": token.collateral_factor,
                    "base_rate": token.base_rate,
                    "rate_multiplier": token.rate_multiplier,
                    "rate_jump_multiplier": token.rate_jump_multiplier,
                    "rate_kink": token.rate_kink,
                    "last_minute": token.last_minute,
                    "contract_value": token.contract_value,
                }
            }
            tokens.append(t)
        return tokens

    @staticmethod
    def convert_token_from_db_to_cache(db_tokens):
        tokens = {}
        for token in db_tokens:
            currency_code = token[0]
            info = token[1]
            a = TokenInfo(total_supply=info.get("total_supply"),
                          total_reserves=info.get("total_reserves"),
                          total_borrows=info.get("total_borrows"),
                          borrow_index=info.get("borrow_index"),
                          oracle_price=info.get("oracle_price"),
                          price=info.get("price"),
                          collateral_factor=info.get("collateral_factor"),
                          base_rate=info.get("base_rate"),
                          rate_multiplier=info.get("rate_multiplier"),
                          rate_jump_multiplier=info.get("rate_jump_multiplier"),
                          rate_kink=info.get("rate_kink"),
                          last_minute=info.get("last_minute"),
                          contract_value=info.get("contract_value"),
                          )
            tokens[currency_code] = a
        return tokens

    def run(self):
        limit = 1000
        self.__class__.VERSION = self.height_table.get_height()
        liquidator_api.accounts = self.convert_token_from_db_to_cache(self.account_table.get_all_accounts())
        liquidator_api.token_infos = self.convert_token_from_db_to_cache(self.token_table.get_all_tokens())

        while True:
            try:
                txs = self.client.get_transactions(self.__class__.VERSION, limit)
                if len(txs) == 0:
                    continue
                for index, tx in enumerate(txs):
                    if tx.get_code_type() != CodeType.BLOCK_METADATA:
                        addrs = liquidator_api.add_tx(tx)
                        if self.state == self.UPDATED:
                            if addrs is not None:
                                for addr in addrs:
                                    self.queue.put(addr)
                self.__class__.VERSION += len(txs)
                if self.state == self.UPDATING and len(txs) < limit:
                    self.state = self.UPDATED
                if self.__class__.VERSION - self.last_version >= 100000:
                    accounts = self.convert_accounts_from_cache_to_db(liquidator_api.accounts)
                    self.account_table.keep_accounts(accounts)
                    tokens = self.convert_token_from_cache_to_db(liquidator_api.token_infos)
                    self.token_table.keep_tokens(tokens)
                    self.height_table.set_height(self.__class__.VERSION)
                    # liquidator_api.update_config(self.__class__.VERSION)
                    # self.last_version = self.__class__.VERSION
            except Exception as e:
                print("chain_scanner", traceback.print_exc())
                print(self.__class__.VERSION)











