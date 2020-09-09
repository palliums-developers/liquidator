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

    def __repr__(self):
        return str(self.amounts)


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

    def __repr__(self):
        return str(self.amounts)

class LiquidationState(IntEnum):
    #正常
    HEALTH = 0
    #这一分钟就需要被清算
    EXPIRED = 1

class AccountView():
    def __init__(self, address, lock_amounts: AccountLockAmounts, borrow_amounts: AccountBorrowAmounts, state):
        self.address = address
        self.lock_amounts = lock_amounts
        self.borrow_amounts = borrow_amounts
        self.state = state

    @classmethod
    def empty(cls, address):
        return cls(address, AccountLockAmounts(), AccountBorrowAmounts(), LiquidationState.HEALTH)

    def get_account_state(self):
        return self.state

    def set_account_state(self, state):
        self.state = state

    def add_borrow(self, sender, currency_code, amount, token_infos):
        if self.address == sender:
            borrow_index = token_infos.get_token_info(currency_code).borrow_index
            self.borrow_amounts.add_amount(currency_code, amount, borrow_index)
            return self.get_liquidator_state(token_infos)

        elif self.lock_amounts.has_currency(currency_code):
            return self.get_liquidator_state(token_infos)

    def add_lock(self, sender, currency_code, amount, token_infos):
        if self.address == sender:
            self.lock_amounts.add_amount(currency_code, amount, token_infos.get_token_info(currency_code).exchange_rate)
            return self.get_liquidator_state(token_infos)

        elif self.lock_amounts.has_currency(currency_code):
            return self.get_liquidator_state(token_infos)

    def add_redeem(self, sender, currency_code, amount, token_infos):
        if self.address == sender:
            self.lock_amounts.reduce_amount(currency_code, amount, token_infos.get_token_info(currency_code).exchange_rate)
            return self.get_liquidator_state(token_infos)

        elif self.lock_amounts.has_currency(currency_code):
            return self.get_liquidator_state(token_infos)

    def add_repay_borrow(self, sender, currency_code, amount, token_infos):
        if self.address == sender:
            self.borrow_amounts.reduce_amount(currency_code, amount, token_infos.get_token_info(currency_code).exchange_rate)
            return self.get_liquidator_state(token_infos)
        elif self.lock_amounts.has_currency(currency_code):
            return self.get_liquidator_state(token_infos)
    
    def add_liquidate_borrow_to_liquidator(self, sender, collateral_currency_code, collateral_amount, token_infos):
        if self.address == sender:
            self.lock_amounts.add_amount(collateral_currency_code, collateral_amount, token_infos.get_token_info(collateral_currency_code).exchange_rate)
            return self.get_liquidator_state(token_infos)

    def add_liquidate_borrow_to_borrower(self, borrower, collateral_currency_code, collateral_amount,
                                         currency_code, amount, token_infos):
        if self.address == borrower:
            self.lock_amounts.reduce_amount(collateral_currency_code, collateral_amount,
                                            token_infos.get_token_info(collateral_currency_code).exchange_rate)
            self.borrow_amounts.reduce_amount(currency_code, amount, token_infos.get_token_info(collateral_currency_code).exchange_rate)
            return self.get_liquidator_state(token_infos)
        elif self.lock_amounts.has_currency(currency_code):
            return self.get_liquidator_state(token_infos)
        
    def get_liquidator_state(self, token_infos):
        nb = self.borrow_amounts.get_total_borrow_value(token_infos)
        nl = self.lock_amounts.get_total_collateral_value(token_infos)
        if nb >= nl:
            return LiquidationState.EXPIRED
        return LiquidationState.HEALTH

class AccountsView():
    def __init__(self):
        self.accounts = dict()
        self.state_accounts = {
            LiquidationState.HEALTH: set(list()),
            LiquidationState.EXPIRED: set(list()),
        }

    def to_json(self):
        ret = dict()
        for account in self.accounts.values():
            ret[account.address] = {
                "state": account.state,
                "lock_amounts": account.lock_amounts,
                "borrow_amounts": account.borrow_amounts,
            }
        return ret

    def get_account_state(self, account_address):
        return self.accounts.get(account_address).get_account_state()

    def get_accounts_of_state(self, liquidation_state):
        return self.state_accounts.get(liquidation_state)

    def add_tx(self, tx: TransactionView, token_infos):
        if not tx.is_successful():
            return
        code_type = tx.get_code_type()
        if code_type == CodeType.PUBLISH:
            state = self.add_publish(tx)
        elif code_type == CodeType.BORROW:
            state =  self.add_borrow(tx, token_infos)
        elif code_type == CodeType.LOCK:
            state =  self.add_lock(tx, token_infos)
        elif code_type == CodeType.REDEEM:
            state =  self.add_redeem(tx, token_infos)
        elif code_type == CodeType.REPAY_BORROW:
            state = self.add_borrow(tx, token_infos)
        return self.set_account_state(tx.get_sender(), state)

    def set_account_state(self, account_address, state):
        if state is not None and account_address is not None:
            pro_state = self.get_account_state(account_address)
            if pro_state is not None:
                self.state_accounts.get(pro_state).remove(account_address)
            self.accounts[account_address].set_account_state = state
            self.state_accounts.get(state).add(account_address)

    def add_publish(self, tx):
        sender = tx.get_sender()
        self.accounts[sender] = AccountView.empty(sender)

    def add_borrow(self, tx, token_infos):
        sender = tx.get_sender()
        currency_code = tx.get_currency_cde()
        amount = tx.get_amount()
        for ac in self.accounts:
            ac.add_borrow(sender, currency_code, amount, token_infos)

    def add_lock(self, tx, token_infos):
        for ac in self.accounts:
            ac.add_lock(tx, token_infos)

    def add_redeem(self, tx, token_infos):
        for ac in self.accounts:
            ac.add_redeem(tx, token_infos)

    def add_repay_borrow(self, tx, token_infos):
        for ac in self.accounts:
            ac.add_repay_borrow(tx, token_infos)
        
    def add_liquidate_borrow(self, tx, token_infos):
        liquidator = self.accounts.get(tx.get_sender())
        borrower = self.accounts.get(tx.get_borrower())
        liquidator.add_liquidate_borrow_to_liquidator(tx.get_sender(), tx.get_collateral_currency_code(), tx.get_collateral_amount(), token_infos)
        borrower.add_liquidate_borrow_to_borrower(tx.get_borrower(), tx.get_collateral_currency_code(), tx.get_collateral_amount(),
                                                  tx.get_currency_code(), tx.get_amount(),
                                                  token_infos)

    def update_liquidation_state(self, token_infos):
        for pro_state, addr in self.state_accounts:
            account = self.accounts.get(addr)
            cur_state = account.get_liquidator_state(token_infos)
            if cur_state != pro_state:
                self.set_account_state(addr, cur_state)
