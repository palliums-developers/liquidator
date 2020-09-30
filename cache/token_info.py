import time
import copy

from .util import new_mantissa, safe_sub, mantissa_mul, mantissa_div

class TokenInfo():
    def __init__(self, **kwargs):
        self.currency_code = kwargs.get("currency_code")
        self.total_supply = kwargs.get("total_supply")
        self.total_reserves = kwargs.get("total_reserves")
        self.total_borrows = kwargs.get("total_borrows")
        self.borrow_index = kwargs.get("borrow_index")

        self.oracle_price = 0
        self.price = kwargs.get("price")

        self.collateral_factor = kwargs.get("collateral_factor")
        self.base_rate = kwargs.get("base_rate")
        self.rate_multiplier = kwargs.get("rate_multiplier")
        self.rate_jump_multiplier = kwargs.get("rate_jump_multiplier")
        self.rate_kink = kwargs.get("rate_kink")
        self.last_minute = kwargs.get("last_minute")

        # resource struct T
        self.contract_value = kwargs.get("contract_value")

        #更新
        self.exchange_rate = self.update_exchange_rate()

    def to_json(self):
        return self.__dict__

    @classmethod
    def from_json(cls, json_value):
        return cls(**json_value)

    @classmethod
    def empty(cls, **kwargs):
        return cls(currency_code=kwargs.get("currency_code"),
                   total_supply=0,
                   total_reserves=0,
                   total_borrows=0,
                   borrow_index=new_mantissa(1, 1),
                   price=0,
                   collateral_factor=kwargs.get("collateral_factor"),
                   base_rate=kwargs.get("base_rate"),
                   rate_multiplier = kwargs.get("rate_multiplier"),
                   rate_jump_multiplier = kwargs.get("rate_jump_multiplier"),
                   rate_kink = kwargs.get("rate_kink"),
                   last_minute = kwargs.get("last_minute") // 60,
                   contract_value = 0)

    def accrue_interest(self, timestamp):
        borrow_rate = self.get_borrow_rate()
        minute = int(timestamp) // 60
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
        print(ret.total_borrows, borrow_rate, type(ret.total_borrows), type(borrow_rate))
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
            return new_mantissa(1, 100)
        self.exchange_rate = new_mantissa(self.contract_value + self.total_borrows - self.total_reserves, self.total_supply)
        return self.exchange_rate

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