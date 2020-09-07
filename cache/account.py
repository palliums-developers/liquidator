from enum import IntEnum

from .token_info import TokenInfos, TokenInfo
from .util import mantissa_div, mantissa_mul

class AccountLockAmounts():
    def __init__(self, **kwargs):
        '''
            币名 = amount
        '''
        self.amounts = kwargs

    def add_amount(self, currency_code, amount, exchange_rate):
        amount = mantissa_div(amount, exchange_rate)
        old_amount = self.amounts.get(currency_code, 0)
        self.amounts[currency_code] = old_amount+amount

    def reduce_amount(self, currency_code, amount, exchange_rate):
        amount = mantissa_div(amount, exchange_rate)
        old_amount = self.amounts.get(currency_code)
        self.amounts[currency_code] = old_amount-amount

    def has_currency(self, currency_code):
        return self.amounts.get(currency_code) is not None

    @staticmethod
    def get_collateral_value(amount, exchange_rate, price, collateral_factor):
        return mantissa_mul(mantissa_mul(mantissa_mul(amount, exchange_rate), collateral_factor), price)

    def get_total_collateral_value(self, **token_infos):
        value = 0
        for currency, amount in self.amounts.items():
            info = token_infos.get(currency)
            collateral_factor = info.get("collateral_factor")
            exchange_rate = info.get("exchange_rate")
            price = info.get("price")
            value += self.get_collateral_value(amount, exchange_rate, price, collateral_factor)
        return value


class AccountBorrowAmounts():
    def __init__(self, amounts):
        '''
        {
            currency_code:(amount, interest_index),
            ...
        }
        :param amounts:
        '''
        self.amounts = amounts

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

class LiquidationState(IntEnum):
    #正常
    HEALTH = 0
    #下一分钟就需要被清算
    UNHEALTH = 1
    #这一分钟就需要被清算
    EXPIRED = 2
    #和以前的状态没有变化
    UNCHHANGE =3

class AccountView():
    def __init__(self, address, lock_amounts: AccountLockAmounts, borrow_amounts: AccountBorrowAmounts):
        self.address = address
        self.lock_amounts = lock_amounts
        self.borrow_amounts = borrow_amounts

    @classmethod
    def empty(cls, address):
        return cls(address, AccountLockAmounts(), AccountBorrowAmounts())

    def add_borrow(self, sender, currency_code, amount, token_infos_now, token_info_a_minute_later):
        if self.address == sender:
            borrow_index = token_infos_now.get_token_info(currency_code).borrow_index
            self.borrow_amounts.add_amount(currency_code, amount, borrow_index)
            return self._get_liquidator_state(token_infos_now, token_info_a_minute_later)

        if self.lock_amounts.has_currency(currency_code) or self.borrow_amounts.has_currency(currency_code):
            return self._get_liquidator_state(token_infos_now, token_info_a_minute_later)

    def add_lock(self, sender, currency_code, amount, token_infos_now, token_info_in_range):
        if self.address == sender:
            self.lock_amounts.add_amount(currency_code, amount, token_infos_now.get_token_info(currency_code).exchange_rate)
            return self._get_liquidator_state(token_infos_now, token_info_in_range)

        if self.lock_amounts.has_currency(currency_code) or self.borrow_amounts.has_currency(currency_code):
            return self._get_liquidator_state(token_infos_now, token_info_in_range)

    def add_redeem(self, sender, currency_code, amount, token_infos_now, token_info_in_range):
        if self.address == sender:
            self.lock_amounts.reduce_amount(currency_code, amount, token_infos_now.get_token_info(currency_code).exchange_rate)
            return self._get_liquidator_state(token_infos_now, token_info_in_range)

        if self.lock_amounts.has_currency(currency_code) or self.borrow_amounts.has_currency(currency_code):
            return self._get_liquidator_state(token_infos_now, token_info_in_range)

    def add_repay_borrow(self, sender, currency_code, amount, token_infos_now, token_info_in_range):
        if self.address == sender:
            self.borrow_amounts.reduce_amount(currency_code, amount, token_infos_now.get_token_info(currency_code).exchange_rate)
            return self._get_liquidator_state(token_infos_now, token_info_in_range)

        if self.lock_amounts.has_currency(currency_code) or self.borrow_amounts.has_currency(currency_code):
            return self._get_liquidator_state(token_infos_now, token_info_in_range)

    def _get_liquidator_state(self, token_infos_now, token_info_a_minute_later: TokenInfos):
        borrows = self.borrow_amounts.get_total_borrow_value(token_info_a_minute_later)
        locks = self.lock_amounts.get_total_collateral_value(token_info_a_minute_later)
        if borrows > locks:
            nb = self.borrow_amounts.get_total_borrow_value(token_infos_now)
            nl = self.lock_amounts.get_total_collateral_value(token_infos_now)
            if nb >= nl:
                return LiquidationState.EXPIRED
            return LiquidationState.UNHEALTH
        return LiquidationState.HEALTH


from violas_client.banktypes.bytecode import CodeType
from violas_client.vlstypes.view import TransactionView


class AccountsView():
    def __init__(self):
        self.accounts = dict()

    def add_tx(self, tx: TransactionView, token_info_now, token_info_a_minute_later):
        if not tx.is_successful():
            return
        if tx.get_code_type() == CodeType.PUBLISH:
            return self.add_publish(tx)
        if tx.get_code_type() == CodeType.BORROW:
            return self.add_borrow(tx, token_info_now, token_info_a_minute_later)
        if tx.get_code_type() == CodeType.LOCK:
            return self.add_lock(tx, token_info_now, token_info_a_minute_later)
        if tx.get_code_type() == CodeType.REDEEM:
            return self.add_redeem(tx, token_info_now, token_info_a_minute_later)
        if tx.get_code_type() == CodeType.REPAY_BORROW:
            return self.add_borrow(tx, token_info_now, token_info_a_minute_later)

    def add_publish(self, tx):
        sender = tx.get_sender()
        self.accounts[sender] = AccountView.empty(sender)

    def add_borrow(self, tx, token_infos_now, token_info_a_minute_later):
        sender = tx.get_sender()
        currency_code = tx.get_currency_cde()
        amount = tx.get_amount()
        for ac in self.accounts:
            ac.add_borrow(sender, currency_code, amount, token_infos_now, token_info_a_minute_later)

    def add_lock(self, tx, token_infos_now, token_info_a_minute_later):
        for ac in self.accounts:
            ac.add_lock(tx, token_infos_now, token_info_a_minute_later)

    def add_redeem(self, tx, token_infos_now, token_info_a_minute_later):
        for ac in self.accounts:
            ac.add_redeem(tx, token_infos_now, token_info_a_minute_later)

    def add_repay_borrow(self, tx):
        pass

    def get_token_infos(self):
        pass

