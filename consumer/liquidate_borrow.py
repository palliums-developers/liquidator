from queue import Queue
from threading import Thread
from violas_client import Client
from cache.util import new_mantissa

class LiquidateBorrowThread(Thread):
    HOLDING_RATIO = 100
    LIQUIDATE_LIMIT = 10

    def __init__(self, queue: Queue, url, faucet_file):
        super(LiquidateBorrowThread, self).__init__()
        self.queue = queue
        self.client = Client.new(url, faucet_file=faucet_file)

    def run(self) -> None:
        while True:
            try:
                addr = self.queue.get()
                self.liquidate_borrow(addr)
            except Exception as e:
                print(e)

    def liquidate_borrow(self, addr):
        collateral_value = self.client.bank_get_total_collateral_value(addr)
        borrow_value = self.client.bank_get_total_borrow_value(addr)
        if collateral_value < borrow_value - self.LIQUIDATE_LIMIT:
            owner_state = self.client.get_account_state(self.client.get_bank_owner_address())
            token_info_stores = owner_state.get_token_info_store_resource()
            lock_amounts = self.client.bank_get_lock_amounts(addr)
            borrow_amounts = self.client.bank_get_borrow_amounts(addr)
            max_lock_currency, max_lock_balance = None, 0
            max_borrow_currency, max_borrow_balance = None, 0

            for currency, amount in lock_amounts.items():
                balance = amount * token_info_stores.get_price(currency)
                if balance > max_lock_balance:
                    max_lock_currency, max_lock_balance = currency, balance

            for currency, amount in borrow_amounts.items():
                balance = amount[1] * token_info_stores.get_price(currency)
                if balance > max_borrow_balance:
                    max_borrow_currency, max_borrow_balance = currency, balance

            borrowed_currency = max_borrow_currency
            collateral_currency = max_lock_currency
            amount = new_mantissa(borrow_value-collateral_value, token_info_stores.get_price(max_lock_currency))
            amount = min(amount, max_lock_balance)

            amounts = self.client.bank_get_amounts()
            bank_amount = amounts.get(borrowed_currency)
            if bank_amount is None or bank_amount < amount*self.HOLDING_RATIO:
                a = self.client.get_balances(self.client.testnet_dd_account.address).get(borrowed_currency)
                if a is None:
                    self.client.add_currency_to_account(self.client.testnet_dd_account, borrowed_currency)
                    self.client.mint_coin(self.client.testnet_dd_account.address, int(amount*self.HOLDING_RATIO))
                elif a < amount:
                    self.client.mint_coin(self.client.testnet_dd_account.address, int(amount*self.HOLDING_RATIO-a))
                if bank_amount is None:
                    bank_amount = 0
                if not self.client.bank_is_published(self.client.testnet_dd_account.address_hex):
                    self.client.bank_publish(self.client.testnet_dd_account)
                self.client.bank_enter(self.client.testnet_dd_account, int(amount*self.HOLDING_RATIO)-bank_amount, currency_code=borrowed_currency)
            self.client.bank_liquidate_borrow(self.client.testnet_dd_account, addr, borrowed_currency, collateral_currency, amount-1)


