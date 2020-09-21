import sys
from enum import IntEnum

from .util import mantissa_div, mantissa_mul
from violas_client.banktypes.bytecode import CodeType
from violas_client.vlstypes.view import TransactionView

class AccountLockAmounts():
    def __init__(self, **kwargs):
        '''
            币名 = amount
        '''
        self.amounts = kwargs

    def add_amount(self, currency_code, amount, exchange_rate):
        amount = mantissa_div(amount, exchange_rate)
        old_amount = self.amounts.get(currency_code, 0)
        print("add_amount", old_amount, amount, exchange_rate)
        self.amounts[currency_code] = old_amount+amount

    def reduce_amount(self, currency_code, amount, exchange_rate):
        amount = mantissa_div(amount, exchange_rate)
        old_amount = self.amounts.get(currency_code)
        print("reduce_amount", old_amount, amount, exchange_rate)
        self.amounts[currency_code] = old_amount-amount

    def has_currency(self, currency_code):
        return self.amounts.get(currency_code) is not None

    @staticmethod
    def get_collateral_value(amount, exchange_rate, price, collateral_factor):
        return mantissa_mul(mantissa_mul(mantissa_mul(amount, exchange_rate), collateral_factor), price)

    def get_total_collateral_value(self, token_infos):
        value = 0
        for currency, amount in self.amounts.items():
            info = token_infos.get(currency)
            collateral_factor = info.collateral_factor
            exchange_rate = info.exchange_rate
            price = info.price
            value += self.get_collateral_value(amount, exchange_rate, price, collateral_factor)
        return value


class AccountBorrowAmounts():
    def __init__(self, **kwargs):
        '''
        {
            currency_code:(amount, interest_index),
            ...
        }
        :param amounts:
        '''
        self.amounts = kwargs

    def add_amount(self, currency_code, amount, interest_index):
        old_amount = self.borrow_balance(currency_code, interest_index)
        amount = amount + old_amount
        self.amounts[currency_code] = (amount, interest_index)

    def reduce_amount(self, currency_code, amount, interest_index):
        old_amount = self.borrow_balance(currency_code, interest_index)
        amount = old_amount - amount
        self.amounts[currency_code] = (amount, interest_index)

    def borrow_balance(self, currency_code, interest_index):
        balance = self.amounts.get(currency_code)
        if balance is not None:
            return mantissa_div(mantissa_mul(balance[0], interest_index), balance[1])
        return 0

    def has_currency(self, currency_code):
        return self.amounts.get(currency_code) is not None

    @staticmethod
    def get_borrow_value(principal, borrow_index, cur_borrow_index, price):
        return mantissa_mul(mantissa_div(mantissa_mul(principal, cur_borrow_index), borrow_index), price)

    def get_total_borrow_value(self, token_infos):
        value = 0
        for currency, (amount, borrow_index) in self.amounts.items():
            info = token_infos.get(currency)
            cur_borrow_index = info.borrow_index
            price = info.price
            value += self.get_borrow_value(amount, borrow_index, cur_borrow_index, price)
        return value


class AccountView():
    def __init__(self, address):
        self.address = address
        self.lock_amounts = AccountLockAmounts()
        self.borrow_amounts = AccountBorrowAmounts()
        self.health = sys.maxsize

    def to_json(self):
        return {
            "address": self.address,
            "lock_amounts": self.lock_amounts.amounts,
            "borrow_amounts": self.borrow_amounts.amounts,
            "health": self.health
        }

    @classmethod
    def from_json(cls, addr, json_value):
        ret = cls(addr)
        lock_amounts = json_value.get("lock_amounts", dict())
        borrow_amounts = json_value.get("borrow_amounts", dict())
        ret.lock_amounts = AccountLockAmounts(**lock_amounts)
        ret.borrow_amounts = AccountBorrowAmounts(**borrow_amounts)
        return ret

    def add_borrow(self, currency_code, amount, token_infos):
        borrow_index = token_infos.get(currency_code).borrow_index
        self.borrow_amounts.add_amount(currency_code, amount, borrow_index)
        self.update_health_state(token_infos)
        return self.health

    def add_lock(self, currency_code, amount, token_infos):
        exchange_rate = token_infos.get(currency_code).exchange_rate
        self.lock_amounts.add_amount(currency_code, amount, exchange_rate)
        self.update_health_state(token_infos)
        return self.health

    def add_redeem(self, currency_code, amount, token_infos):
        exchange_rate = token_infos.get(currency_code).exchange_rate
        self.lock_amounts.reduce_amount(currency_code, amount, exchange_rate)
        self.update_health_state(token_infos)
        return self.health

    def add_repay_borrow(self, currency_code, amount, token_infos):
        borrow_index = token_infos.get(currency_code).borrow_index
        self.borrow_amounts.reduce_amount(currency_code, amount, borrow_index)
        self.update_health_state(token_infos)
        return self.health
    
    def add_liquidate_borrow_to_liquidator(self, collateral_currency_code, collateral_amount, token_infos):
        exchange_rate = token_infos.get(collateral_currency_code).exchange_rate
        self.lock_amounts.add_amount(collateral_currency_code, collateral_amount, exchange_rate)
        self.update_health_state(token_infos)
        return self.health

    def add_liquidate_borrow_to_borrower(self, collateral_currency_code, collateral_amount,
                                         currency_code, amount, token_infos):
        self.lock_amounts.reduce_amount(collateral_currency_code, collateral_amount,
                                        token_infos.get(collateral_currency_code).exchange_rate)
        self.borrow_amounts.reduce_amount(currency_code, amount, token_infos.get(collateral_currency_code).exchange_rate)
        self.update_health_state(token_infos)
        return self.health

    def has_borrow_any(self):
        for currency, amount in self.borrow_amounts.amounts.items():
            if amount[0] > 0:
                return True
        return False

    def has_borrow(self, currency_code):
        return self.borrow_amounts.amounts.get(currency_code) is not None

    def has_lock_any(self):
        return len(self.lock_amounts.amounts)

    def has_lock(self, currency_code):
        return self.lock_amounts.amounts.get(currency_code) is not None

    def get_total_borrow_value(self, token_infos):
        return self.borrow_amounts.get_total_borrow_value(token_infos)

    def get_total_collateral_value(self, token_infos):
        return self.lock_amounts.get_total_collateral_value(token_infos)

    def update_health_state(self, token_infos):
        if self.has_borrow_any():
            borrow_value = self.borrow_amounts.get_total_borrow_value(token_infos)
            collateral_value = self.lock_amounts.get_total_collateral_value(token_infos)
            self.health = collateral_value / borrow_value
            return self.health
        return sys.maxsize