import time
import copy
from dataclasses import dataclass
from .base import Base

from .util import new_mantissa, safe_sub, mantissa_mul, mantissa_div

@dataclass

class TokenInfo(Base):
    PREFIX = "token"

    currency_code: str
    price: int = 0
    total_supply: int = 0
    total_reserves: int = 0
    total_borrows: int = 0
    oracle_price: int = None
    collateral_factor: int = None
    base_rate: int = None
    rate_multiplier: int = None
    rate_jump_multiplier: int = None
    rate_kink: int = None
    last_minute: int = None
    # resource struct T
    contract_value: int = 0
    borrow_index: int = new_mantissa(1, 1)


    @classmethod
    def empty(cls, **kwargs):
        return cls(currency_code=kwargs.get("currency_code"),
                   total_supply=kwargs.get("total_supply", 0),
                   total_reserves=kwargs.get("total_reserves", 0),
                   total_borrows=kwargs.get("total_borrows", 0),
                   oracle_price= kwargs.get("oracle_price", 0),
                   borrow_index=kwargs.get("borrow_index", new_mantissa(1, 1)),
                   price=kwargs.get("price", 0),
                   collateral_factor=kwargs.get("collateral_factor"),
                   base_rate=kwargs.get("base_rate"),
                   rate_multiplier=kwargs.get("rate_multiplier"),
                   rate_jump_multiplier=kwargs.get("rate_jump_multiplier"),
                   rate_kink=kwargs.get("rate_kink"),
                   last_minute = kwargs.get("last_minute"),
                   contract_value = kwargs.get("contract_value", 0))

    def accrue_interest(self, timestamp):
        borrow_rate = self.get_borrow_rate()
        minute = int(timestamp // 60)
        cnt = safe_sub(minute, self.last_minute)
        if cnt <= 0:
            return self
        borrow_rate = borrow_rate *cnt
        self.last_minute = minute
        interest_accumulated = mantissa_mul(self.total_borrows, borrow_rate)
        self.total_borrows = self.total_borrows + interest_accumulated
        reserve_factor = new_mantissa(1, 20)
        self.total_reserves = self.total_reserves +mantissa_mul(interest_accumulated, reserve_factor)
        self.borrow_index = self.borrow_index + mantissa_mul(self.borrow_index, borrow_rate)
        return self

    def get_forecast(self, time_minute):
        ret = copy.deepcopy(self)
        borrow_rate = ret.get_borrow_rate()
        minute = time_minute
        cnt = safe_sub(minute, ret.last_minute)
        if cnt <= 0:
            return ret
        borrow_rate = borrow_rate * cnt
        ret.last_minute = minute
        interest_accumulated = mantissa_mul(ret.total_borrows, borrow_rate)
        ret.total_borrows = ret.total_borrows + interest_accumulated
        reserve_factor = new_mantissa(1, 20)
        ret.total_reserves = ret.total_reserves + mantissa_mul(interest_accumulated, reserve_factor)
        ret.borrow_index = ret.borrow_index + mantissa_mul(ret.borrow_index, borrow_rate)
        return ret

    def get_borrow_rate(self):
        if self.total_borrows == 0:
            util = 0
        else:
            util = new_mantissa(self.total_borrows, self.total_borrows + safe_sub(self.contract_value, self.total_reserves))
        if util < self.rate_kink:
            return mantissa_mul(self.rate_multiplier, util) + self.base_rate
        normal_rate = mantissa_mul(self.rate_multiplier, self.rate_kink) + self.base_rate
        excess_util = util - self.rate_kink
        return mantissa_mul(self.rate_jump_multiplier, excess_util) + normal_rate

    def update_exchange_rate(self):
        if self.total_supply == 0:
            self.exchange_rate = new_mantissa(1, 100)
            return self.exchange_rate
        self.exchange_rate = new_mantissa(self.contract_value + self.total_borrows - self.total_reserves, self.total_supply)
        return self.exchange_rate

    def get_exchange_rate(self):
        if hasattr(self, "exchange_rate"):
            return self.exchange_rate
        return self.update_exchange_rate()

    def get_cur_exchange_rate(self):
        ret = self.get_forecast(int(time.time() // 60))
        return ret.get_exchange_rate()

    def add_lock(self, tx):
        amount = tx.get_amount()
        self.contract_value += amount
        tokens = mantissa_div(amount, self.exchange_rate)
        self.total_supply += tokens

    def add_borrow(self, tx):
        amount = tx.get_amount()
        self.total_borrows += amount
        self.contract_value -= amount

    def add_redeem(self, tx):
        amount = tx.get_amount()
        tokens = mantissa_div(amount, self.exchange_rate)
        self.total_supply = safe_sub(self.total_supply, tokens)
        self.contract_value -= amount

    def add_repay_borrow(self, tx):
        amount = tx.get_amount()
        self.total_borrows = safe_sub(self.total_borrows, amount)
        self.contract_value += amount

    def add_liquidate_borrow(self, tx):
        self.add_repay_borrow(tx)