import time
from queue import Queue
from threading import Thread
from bank.util import new_mantissa, mantissa_mul, mantissa_div
from bank import Bank
from network import (
    create_violas_client,
    get_liquidator_account,
    mint_coin_to_liquidator_account,
    DEFAULT_COIN_NAME,
    DD_ADDR
)

# 清算的最小值
LIQUIDATE_LIMIT = 1_000
# 每次mint的值
MIN_MINT_PRICE = 20_000_000
#VLS最小值
MIN_VLS_AMOUNT = 1000
#拥有的最大值
MAX_OWN_PRICE = 10_000_000


class LiquidateBorrowThread(Thread):

    def __init__(self, queue: Queue):
        super(LiquidateBorrowThread, self).__init__()
        self.queue = queue
        self.client = create_violas_client()
        self.bank_account = get_liquidator_account()

    def run(self) -> None:
        while True:
            # try:
                addr = self.queue.get()
                self.liquidate_borrow(addr)
            # except Exception as e:
            #     print("liquidator_thread", e)
            #     time.sleep(2)


    def liquidate_borrow(self, addr):
        if self.client.get_balance(self.bank_account.address_hex, DEFAULT_COIN_NAME) < MIN_VLS_AMOUNT:
            mint_coin_to_liquidator_account(self.bank_account, DEFAULT_COIN_NAME, MIN_MINT_PRICE)
            return
        collateral_value = self.client.bank_get_total_collateral_value(addr)
        borrow_value = self.client.bank_get_total_borrow_value(addr)
        if collateral_value < borrow_value - LIQUIDATE_LIMIT:
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
            bank_amount = mantissa_mul(self.client.bank_get_amount(self.bank_account.address_hex, borrowed_currency), token_info_stores.get_price(borrowed_currency))
            if bank_amount is None or bank_amount < amount:
                a = self.client.get_balances(self.bank_account.address).get(borrowed_currency)
                if a is None or a < amount:
                    mint_coin_to_liquidator_account(self.bank_account, borrowed_currency, mantissa_div(max(amount, MIN_MINT_PRICE), token_info_stores.get_price(borrowed_currency)))
                    return
                if not self.client.bank_is_published(self.bank_account.address_hex):
                    self.client.bank_publish(self.bank_account)
                currency_amount = self.client.get_balance(self.bank_account.address_hex, currency_code=borrowed_currency)
                self.client.bank_enter(self.bank_account, currency_amount-100_000, currency_code=borrowed_currency)
            cs = self.client.get_account_registered_currencies(self.bank_account.address_hex)
            if collateral_currency not in cs:
                self.client.add_currency_to_account(self.bank_account, collateral_currency)
            self.client.bank_liquidate_borrow(self.bank_account, addr, borrowed_currency, collateral_currency, mantissa_div(amount, token_info_stores.get_price(collateral_currency)-1))


class BackLiquidatorThread(Thread):
    # 拥有的最大的值
    INTERVAL_TIME = 60

    def __init__(self):
        super(BackLiquidatorThread, self).__init__()
        self.client = create_violas_client()
        self.bank_account = get_liquidator_account()

    def run(self) -> None:
        while True:
            balances = self.client.bank_get_amounts(self.bank_account.address_hex)
            for currency, amount in balances.items():
                price = mantissa_mul(amount, Bank().get_price(currency))
                if price > MAX_OWN_PRICE:
                    self.client.bank_exit(self.bank_account, amount, currency)
                    balance = self.client.get_balance(self.bank_account.address_hex, currency)
                    self.client.transfer_coin(self.bank_account, DD_ADDR, balance)
            balances = self.client.get_balances(self.bank_account.address_hex)
            for currency, amount in balances.items():
                if currency == DEFAULT_COIN_NAME:
                    price = amount
                else:
                    price = mantissa_mul(amount, Bank().get_price(currency))
                if price > MAX_OWN_PRICE:
                    self.client.transfer_coin(self.bank_account, DD_ADDR, amount, currency_code=currency)
            time.sleep(self.INTERVAL_TIME)
            

if __name__ == "__main__":
    q = Queue()
    t = LiquidateBorrowThread(q)
    t.liquidate_borrow("2F396FCBE88A27F0FC05934BBEF3687B")
