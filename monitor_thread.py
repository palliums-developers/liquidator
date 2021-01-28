import time
import copy
import traceback
from threading import Thread
from network import create_violas_client
from bank import Bank
from bank.bank import bank_lock

class MonitorThread(Thread):
    INTERVAL = 60

    def __init__(self):
        super().__init__()
        self.client = create_violas_client()
        self.bank = Bank()

    def run(self):
        while True:
            try:
                bank_lock.acquire()
                version = self.bank.height
                local_token_infos = copy.deepcopy(self.bank.token_infos)
                accounts = copy.deepcopy(self.bank.accounts)
                bank_lock.release()
                time.sleep(self.INTERVAL)
                chain_token_infos = self.client.get_account_state(self.client.get_bank_owner_address(), version).get_token_info_store_resource(accrue_interest=False).tokens
                currencies = self.client.bank_get_registered_currencies(True)
                for currency in currencies:
                    index = self.client.bank_get_currency_index(currency_code=currency)
                    currency_info = chain_token_infos[index: index+2]
                    index = self.client.bank_get_currency_index(currency)
                    state = self.client.get_account_state(self.client.BANK_OWNER_ADDRESS, version)
                    contract_value = state.get_bank_amount(index)
                    self.assert_token_consistence(local_token_infos, currency, currency_info, contract_value)
                for addr in accounts.keys():
                    self.assert_account_consistence(addr, accounts, self.client.get_account_state(addr, version).get_tokens_resource())
            except Exception as e:
                print("monitor_thread")
                traceback.print_exc()
                time.sleep(2)

    def assert_account_consistence(self, local_accounts, address, tokens):
        # print(f"check {address}")
        if isinstance(address, bytes):
            address = address.hex()
        i = 0
        while len(tokens.borrows) > i:
            currency = self.client.bank_get_currency_code(i)
            borrows = local_accounts[address].borrow_amounts.amounts.get(currency)
            if borrows is None:
                assert tokens.borrows[i].principal == 0
            else:
                assert tokens.borrows[i].principal == borrows[0]
                assert tokens.borrows[i].interest_index == borrows[1]
            i += 2

        i = 0
        while len(tokens.borrows) > i:
            currency = self.client.bank_get_currency_code(i)
            locks = local_accounts[address].lock_amounts.amounts
            value = locks.get(currency)
            if value is None:
                value = 0
            #存款数据
            assert tokens.ts[i+1].value == value
            i +=2

    def assert_token_consistence(self, local_token_infos, currency, token_infos, contract_value):
        # print(f"checkout {currency}")
        local_info = local_token_infos.get(currency)
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
        assert contract_value == local_info.contract_value
