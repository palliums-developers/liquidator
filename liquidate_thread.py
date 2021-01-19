import time
from queue import Queue
from threading import Thread, Lock
from bank.util import new_mantissa, mantissa_mul, mantissa_div
from bank import Bank
import traceback
from network import (
    create_violas_client,
    get_liquidator_account,
    mint_coin_to_liquidator_account,
    DEFAULT_COIN_NAME,
    DD_ADDR
)

# 清算的最小值
LIQUIDATE_LIMIT = 10_000_000
# 每次mint的值
MIN_MINT_VALUE = 200_000_000
#VLS最小值
MIN_VLS_AMOUNT = 1_000
#拥有的最大值
MAX_OWN_VALUE = 1_000_000_000
lock = Lock()


class LiquidateBorrowThread(Thread):

    def __init__(self, queue: Queue):
        super(LiquidateBorrowThread, self).__init__()
        self.queue = queue
        self.client = create_violas_client()
        self.bank_account = get_liquidator_account()
        self.bank = Bank()

    def run(self) -> None:
        while True:
            addr = self.queue.get()
            try:
                lock.acquire()
                self.liquidate_borrow(addr)
            except Exception as e:
                print("liquidator_thread")
                traceback.print_exc()
                time.sleep(1)
            finally:
                lock.release()

    def mint_coin(self, account, currency_code, amount, currency_id=None):
        print("mint coin",currency_code, amount, currency_id)
        if currency_id is not None:
            id = self.bank.get_currency_id(currency_code)
            if currency_id <= id:
                return
        return mint_coin_to_liquidator_account(account, currency_code, amount, currency_id)

    def liquidate_borrow(self, addr):
        if self.client.get_balance(self.bank_account.address_hex, DEFAULT_COIN_NAME) < MIN_VLS_AMOUNT:
            self.mint_coin(self.bank_account, DEFAULT_COIN_NAME, MIN_MINT_VALUE)
            return
        collateral_value = self.client.bank_get_total_collateral_value(addr)
        borrow_value = self.client.bank_get_total_borrow_value(addr)
        if collateral_value < borrow_value - LIQUIDATE_LIMIT:
            owner_state = self.client.get_account_state(self.client.get_bank_owner_address())
            token_info_stores = owner_state.get_token_info_store_resource()
            lock_amounts = self.client.bank_get_lock_amounts(addr)
            borrow_amounts = self.client.bank_get_borrow_amounts(addr)
            max_lock_currency, max_lock_value = None, 0
            max_borrow_currency, max_borrow_value = None, 0

            for currency, amount in lock_amounts.items():
                balance = mantissa_mul(amount, token_info_stores.get_price(currency))
                if balance > max_lock_value:
                    max_lock_currency, max_lock_value = currency, balance

            for currency, amount in borrow_amounts.items():
                balance = mantissa_mul(amount[1], token_info_stores.get_price(currency))
                if balance > max_borrow_value:
                    max_borrow_currency, max_borrow_value = currency, balance

            borrowed_currency = max_borrow_currency
            collateral_currency = max_lock_currency
            owe_value = borrow_value - collateral_value
            owe_value = min(owe_value, max_lock_value)
            bank_value = mantissa_mul(self.client.bank_get_amount(self.bank_account.address_hex, borrowed_currency), token_info_stores.get_price(borrowed_currency))
            owe_amount = mantissa_div(owe_value, Bank().get_price(borrowed_currency))
            if bank_value is None or bank_value < owe_value:
                a = self.client.get_balances(self.bank_account.address).get(borrowed_currency)
                if a is None or a < owe_amount:
                    self.mint_coin(self.bank_account, borrowed_currency, mantissa_div(max(owe_value, MIN_MINT_VALUE), token_info_stores.get_price(borrowed_currency)), self.bank.get_currency_id(borrowed_currency))
                    return
                if not self.client.bank_is_published(self.bank_account.address_hex):
                    self.client.bank_publish(self.bank_account)
                currency_amount = self.client.get_balance(self.bank_account.address_hex, currency_code=borrowed_currency)
                self.client.bank_enter(self.bank_account, currency_amount, currency_code=borrowed_currency)
            cs = self.client.get_account_registered_currencies(self.bank_account.address_hex)
            if collateral_currency not in cs:
                self.client.add_currency_to_account(self.bank_account, collateral_currency)
            try:
                self.client.bank_liquidate_borrow(self.bank_account, addr, borrowed_currency, collateral_currency, int(owe_amount*0.9))
            except Exception as e:
                traceback.print_exc()
                print(addr, borrowed_currency, collateral_currency, owe_amount)
            self.bank.add_currency_id(borrowed_currency)

class BackLiquidatorThread(Thread):
    # 拥有的最大的值
    INTERVAL_TIME = 61

    def __init__(self):
        super(BackLiquidatorThread, self).__init__()
        self.client = create_violas_client()
        self.bank_account = get_liquidator_account()
        self.back_currencies = {}

    def run(self) -> None:

        while True:

            lock.acquire()
            try:
                balances = self.client.bank_get_amounts(self.bank_account.address_hex)
                for currency, amount in balances.items():
                    price = Bank().get_price(currency)
                    value = mantissa_mul(amount, price)
                    if value > MAX_OWN_VALUE:
                        amount = mantissa_div(value-MIN_MINT_VALUE, price)
                        self.client.bank_exit(self.bank_account, amount, currency)
                        Bank().add_currency_id(currency)

                balances = self.client.get_balances(self.bank_account.address_hex)
                for currency, amount in balances.items():
                    if currency == DEFAULT_COIN_NAME:
                        price = new_mantissa(1, 1)
                    else:
                        price = Bank().get_price(currency)
                    value = mantissa_mul(amount, price)
                    if value > MAX_OWN_VALUE:
                        if self.get_back_num(currency) < 2:
                            self.add_back_num(currency)
                            continue
                        if currency == DEFAULT_COIN_NAME:
                            amount = mantissa_div(value - MIN_MINT_VALUE, price)
                        else:
                            amount = mantissa_div(value, price)
                        self.client.transfer_coin(self.bank_account, DD_ADDR, amount, currency_code=currency)
                    self.set_back_num(currency, 0)
            except Exception as e:
                import traceback
                print("back_liquidator_thread", e)
                traceback.print_exc()
                time.sleep(2)
            finally:
                lock.release()
                time.sleep(self.INTERVAL_TIME)

    def get_back_num(self, currency):
        return self.back_currencies.get(currency, 0)

    def set_back_num(self, currency, num):
        self.back_currencies[currency] = num

    def add_back_num(self, currency):
        num = self.get_back_num(currency)
        self.set_back_num(currency, num+1)
            

if __name__ == "__main__":
    q = Queue()
    t = BackLiquidatorThread()
    t.run()
