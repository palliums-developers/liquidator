import time
from queue import Queue
from threading import Thread, Lock
from bank.util import new_mantissa, mantissa_mul, mantissa_div
from bank import Bank
import traceback
from coin_porter import CoinPorter
from network import (
    create_violas_client,
    get_liquidator_account,
    DEFAULT_COIN_NAME,
    DD_ADDR
)

# 清算的最小值
LIQUIDATE_LIMIT = 10_000_000
# 每次mint的值
MIN_MINT_VALUE = 1_000_000_000
#VLS最小值
MIN_VLS_AMOUNT = 1_000
#拥有的最大值
MAX_OWN_VALUE = 10_000_000_000
lock = Lock()

class LiquidateBorrowThread(Thread):

    def __init__(self, queue: Queue):
        super(LiquidateBorrowThread, self).__init__()
        self.queue = queue
        self.client = create_violas_client()
        self.bank_account = get_liquidator_account()
        self.bank = Bank()
        self.coin_porter = CoinPorter()

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

    def get_max_lock_currency(self, addr):
        max_lock_currency, max_lock_value = None, 0
        for currency in self.bank.accounts.get(addr).lock_amounts.amounts.keys():
            balance = mantissa_mul(self.bank.get_lock_amount(addr, currency), self.bank.get_oracle_price(currency))
            if balance > max_lock_value:
                max_lock_currency, max_lock_value = currency, balance
        return max_lock_currency, max_lock_value

    def get_max_borrow_currency(self, addr):
        borrow_amounts = self.bank.accounts.get(addr).borrow_amounts.amounts
        max_borrow_currency, max_borrow_value = None, 0
        for currency in borrow_amounts.keys():
            balance = mantissa_mul(self.bank.get_borrow_amount(addr, currency), self.bank.get_oracle_price(currency))
            if balance > max_borrow_value:
                max_borrow_currency, max_borrow_value = currency, balance
        return max_borrow_currency, max_borrow_value

    def try_enter_bank(self, ac, currency_code, min_amount):
        amount = self.client.get_balance(ac.address, currency_code)
        if amount < min_amount:
            return 0
        if not self.client.bank_is_published(ac.address):
            self.client.bank_publish(ac)

        self.client.bank_enter(self.bank_account, amount, currency_code=currency_code)
        return amount
    
    def try_redeem(self, ac, currency_code, min_amount):
        amount = self.client.bank_get_lock_amount(ac.address, currency_code)
        if amount < min_amount:
            return 0
        self.client.bank_redeem(ac, amount, currency_code)
        return amount

    def try_apply_coin(self, ac, currency_code, amount):
        self.coin_porter.try_apply_coin(ac, currency_code, amount)

    def liquidate_borrow(self, addr):
        bank_account_state = self.client.get_account_state(self.bank_account.address)

        '''vls币是否足够，用作 gas fee'''
        if bank_account_state.get_balance(DEFAULT_COIN_NAME) < MIN_VLS_AMOUNT:
            self.try_apply_coin(self.bank_account, DEFAULT_COIN_NAME, MIN_MINT_VALUE)

        lock_value = self.bank.accounts.get(addr).total_lock
        borrow_value = self.bank.accounts.get(addr).total_borrow
        owe_value = borrow_value - lock_value
        if owe_value > LIQUIDATE_LIMIT:
            ''' 获取清算的币和偿还的币，以获取清算的最大金额 '''
            max_lock_currency, max_lock_value = self.get_max_lock_currency(addr)
            max_borrow_currency, max_borrow_value = self.get_max_borrow_currency(addr)
            liquidate_value = min(owe_value, max_lock_value, max_borrow_value)

            '''账户余额是否足够清算'''
            borrow_currency_price = self.bank.get_oracle_price(max_borrow_currency)
            bank_value = mantissa_mul(self.client.bank_get_amount(self.bank_account.address_hex, max_borrow_currency), borrow_currency_price)
            if bank_value < LIQUIDATE_LIMIT:
                amount = mantissa_div(LIQUIDATE_LIMIT, borrow_currency_price)
                if self.try_redeem(self.bank_account, max_borrow_currency, amount) <= 0 and self.try_enter_bank(self.bank_account, max_borrow_currency, amount) <= 0:
                    value = max(MIN_MINT_VALUE, liquidate_value)
                    amount = mantissa_div(value, borrow_currency_price)
                    self.try_apply_coin(self.bank_account, max_borrow_currency, amount)
                return

            liquidate_value = min(bank_value, liquidate_value)
            liquidate_amount = int(mantissa_div(liquidate_value, borrow_currency_price)*0.9)

            '''是否已经注册偿还的币'''
            cs = self.client.get_account_registered_currencies(self.bank_account.address)
            if max_lock_currency not in cs:
                self.client.add_currency_to_account(self.bank_account, max_lock_currency)

            try:
                self.client.bank_liquidate_borrow(self.bank_account, addr, max_borrow_currency, max_lock_currency, liquidate_amount)
            except Exception as e:
                localtime = time.asctime(time.localtime(time.time()))
                traceback.print_exc()
                print(localtime, addr, max_borrow_currency, max_lock_currency, liquidate_amount)
            finally:
                self.coin_porter.add_last_liquidate_id(max_borrow_currency)
                # print("liquidator_id:", self.coin_porter.last_liquidate_ids)
                # print("apply_id:", self.coin_porter.last_apply_ids)

class BackLiquidatorThread(Thread):
    # 拥有的最大的值
    INTERVAL_TIME = 61

    def __init__(self):
        super(BackLiquidatorThread, self).__init__()
        self.client = create_violas_client()
        self.bank_account = get_liquidator_account()
        self.coin_porter = CoinPorter()
        self.bank = Bank()

    def run(self) -> None:
        while True:
            lock.acquire()
            try:
                self.try_redeem()
                self.try_exit_bank()
                self.try_back_coin()
            except Exception as e:
                print("back_liquidator_thread")
                traceback.print_exc()
                time.sleep(2)
            finally:
                lock.release()
                time.sleep(self.INTERVAL_TIME)


    def try_exit_bank(self):
        balances = self.client.bank_get_amounts(self.bank_account.address)
        for currency, amount in balances.items():
            last_liquidate_time = self.coin_porter.get_last_liquidate_time(currency)
            cur_time = time.time()
            if cur_time - last_liquidate_time > 2*self.INTERVAL_TIME:
                price = self.bank.get_price(currency)
                value = mantissa_mul(amount, price)
                if value > MAX_OWN_VALUE:
                    amount = mantissa_div(value - MIN_MINT_VALUE, price)
                    self.client.bank_exit(self.bank_account, amount, currency)

    def try_redeem(self):
        balances = self.client.bank_get_lock_amounts(self.bank_account.address)
        for currency, amount in balances.items():
            last_liquidate_time = self.coin_porter.get_last_liquidate_time(currency)
            cur_time = time.time()
            if cur_time - last_liquidate_time > 2*self.INTERVAL_TIME:
                price = self.bank.get_price(currency)
                value = mantissa_mul(amount, price)
                if value > MAX_OWN_VALUE:
                    amount = mantissa_div(value - MIN_MINT_VALUE, price)
                    self.client.bank_redeem(self.bank_account, amount, currency)

    def try_back_coin(self):
        balances = self.client.get_balances(self.bank_account.address)
        for currency, amount in balances.items():
            if currency == DEFAULT_COIN_NAME:
                if amount > MAX_OWN_VALUE:
                    self.client.transfer_coin(self.bank_account, DD_ADDR, amount-MIN_VLS_AMOUNT)
                continue

            cur_time = time.time()
            last_liquidate_time = self.coin_porter.get_last_liquidate_time(currency)
            if cur_time - last_liquidate_time > 2*self.INTERVAL_TIME:
                price = self.bank.get_price(currency)
                value = mantissa_mul(amount, price)
                if value > MAX_OWN_VALUE:
                    self.client.transfer_coin(self.bank_account, DD_ADDR, amount)




if __name__ == "__main__":
    q = Queue()
    t = LiquidateBorrowThread(q)
    t.liquidate_borrow("0003d51002e8aaaa8e9016fbb3d11165")
