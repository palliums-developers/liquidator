from queue import Queue
from threading import Thread
from violas_client import Client
from bank.util import new_mantissa
from network import (
    create_http_client,
    create_violas_client,
    get_liquidator_account,
    mint_coin_to_liquidator_account,
    DEFAULT_COIN_NAME,
    DD_ADDR
)

class LiquidateBorrowThread(Thread):
    HOLDING_RATIO = 10
    LIQUIDATE_LIMIT = 1_000_000
    MIN_MINT_AMOUNT = 2_000_000_000
    MAX_OWN_AMOUNT = 1_000_000_000
    MIN_VLS_AMOUNT = 1_000_000

    def __init__(self, queue: Queue):
        super(LiquidateBorrowThread, self).__init__()
        self.queue = queue
        self.client = create_violas_client()
        self.bank_account = get_liquidator_account()

    def run(self) -> None:
        while True:
            try:
                addr = self.queue.get()
                self.liquidate_borrow(addr)
            except Exception as e:
                print(e)

    def liquidate_borrow(self, addr):
        if self.client.get_balance(self.bank_account.address_hex, DEFAULT_COIN_NAME) < self.MIN_VLS_AMOUNT:
            mint_coin_to_liquidator_account(self.bank_account, DEFAULT_COIN_NAME, self.MIN_MINT_AMOUNT)
            return
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
            bank_amount = self.client.bank_get_amount(self.bank_account.address_hex, borrowed_currency)
            if bank_amount is None or bank_amount < amount*self.HOLDING_RATIO:
                a = self.client.get_balances(self.bank_account.address).get(borrowed_currency)
                if a is None or a < amount:
                    mint_coin_to_liquidator_account(self.bank_account, max(self.MIN_MINT_AMOUNT, int(amount*self.HOLDING_RATIO)))
                    return
                if not self.client.bank_is_published(self.bank_account.address_hex):
                    self.client.bank_publish(self.bank_account)
                currency_amount = self.client.get_balance(borrowed_currency)
                self.client.bank_enter(self.bank_account, currency_amount-100_000, currency_code=borrowed_currency)
            cs = self.client.get_account_registered_currencies(self.bank_account.address_hex)
            if collateral_currency not in cs:
                self.client.add_currency_to_account(self.bank_account, collateral_currency)
            self.client.bank_liquidate_borrow(self.bank_account, addr, borrowed_currency, collateral_currency, amount-1)
            amount = self.client.bank_get_amount(self.bank_account.address_hex, collateral_currency)
            if amount > self.MAX_OWN_AMOUNT:
                self.client.bank_exit(self.bank_account, collateral_currency, amount-100)
                self.client.transfer_coin(self.bank_account, DD_ADDR, amount-100)


