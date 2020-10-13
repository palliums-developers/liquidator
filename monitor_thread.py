import time
from threading import Thread
from conf.config import URL
from violas_client import Client
from cache.api import liquidator_api

class MonitorThread(Thread):
    INTERVAL = 60

    def __init__(self):
        super().__init__()
        self.client = Client.new(URL)

    def run(self):
        while True:
            time.sleep(self.INTERVAL)
            try:
                token_infos = self.client.get_account_state(self.client.get_bank_owner_address()).get_token_info_store_resource(accrue_interest=False).tokens
                accounts = liquidator_api.accounts
                currencies = self.client.bank_get_registered_currencies(True)
                for currency in currencies:
                    try:
                        index = self.client.bank_get_currency_index(currency_code=currency)
                        currency_info = token_infos[index*2: index*2+2]
                        self.assert_token_consistence(currency, currency_info)
                    except Exception as e:
                        print(currency, index, currency_info)
                for addr in accounts.keys():
                    self.assert_account_consistence(addr, token_infos)
            except Exception as e:
                import traceback
                print("monitor_thread", traceback.print_exc())

    def assert_account_consistence(self, address, tokens):
        if isinstance(address, bytes):
            address = address.hex()
        i = 0
        while len(tokens.borrows) > i:
            currency = self.client.bank_get_currency_code(i)
            borrows = liquidator_api.accounts[address].borrow_amounts.amounts.get(currency)
            if borrows is None:
                assert tokens.borrows[0].principal == 0
            else:
                assert tokens.borrows[0].principal == borrows[0]
                assert tokens.borrows[0].interest_index == borrows[1]
            i += 2

        i = 0
        while len(tokens.borrows) > i:
            currency = self.client.bank_get_currency_code(i)
            locks = liquidator_api.accounts[address].lock_amounts.amounts
            #存款数据
            assert tokens.ts[i+1].value == locks[currency]

    @staticmethod
    def assert_token_consistence(currency, token_infos):
        local_info = liquidator_api.get_token_info(currency)
        assert token_infos[1].total_supply == local_info.total_supply
        assert token_infos[0].total_reserves == local_info.total_reserves
        assert token_infos[0].total_borrows == local_info.total_borrows
        assert token_infos[0].borrow_index == local_info.borrow_index
        assert token_infos[0].price == local_info.price
        assert token_infos[0].collateral_factor == local_info.collateral_factor
        assert token_infos[0].base_rate == local_info.base_rate
        assert token_infos[0].rate_multiplier == local_info.rate_multiplier
        assert token_infos[0].rate_jump_multiplier == local_info.rate_jump_multiplier
        assert token_infos[0].rate_kink == local_info.rate_kink
        assert token_infos[0].last_minute == local_info.last_minute

# monitor_thread = MonitorThread()
# monitor_thread.setDaemon(False)
# monitor_thread.start()