
from enum import IntEnum



class LiquidationState(IntEnum):
    NO_CHANGE = 0
    NOW = 1
    IN_RANGE = 2
    OUT_OF_RANGE = 3

class AccountView():
    def __init__(self, address, lock_amounts: LockAmounts, borrow_amounts: BorrowAmounts):
        self.address = address
        self.lock_amounts = lock_amounts
        self.borrow_amounts = borrow_amounts
        
    @classmethod
    def empty(cls, address):
        return cls(address, LockAmounts({}), BorrowAmounts({}))
        
    def add_borrow(self, sender, currency_code, amount, token_infos_now, token_infos_in_range):
        if self.address == sender:
            self.borrow_amounts.add_amount(currency_code, amount)
            return self._get_liquidator_state(token_infos_now, token_infos_in_range)

        if self.lock_amounts.has_currency(currency_code) or self.borrow_amounts.has_currency(currency_code):
            return self._get_liquidator_state(token_infos_now, token_infos_in_range)

        return LiquidationState.NO_CHANGE

    def add_lock(self, sender, currency_code, amount, token_info_now, token_info_in_range):
        if self.address == sender:
            self.lock_amounts.add_amount(currency_code, amount, token_info_now.get(currency_code))
            return self._get_liquidator_state(token_info_now, token_info_in_range)

        if self.lock_amounts.has_currency(currency_code) or self.borrow_amounts.has_currency(currency_code):
            return self._get_liquidator_state(token_info_now, token_info_in_range)

        return LiquidationState.NO_CHANGE

    def add_redeem(self, sender, currency_code, amount, token_info_now, token_info_in_range):
        if self.address == sender:
            self.lock_amounts.reduce_amount(currency_code, amount, token_info_now.get(currency_code))
            return self._get_liquidator_state(token_info_now, token_info_in_range)

        if self.lock_amounts.has_currency(currency_code) or self.borrow_amounts.has_currency(currency_code):
            return self._get_liquidator_state(token_info_now, token_info_in_range)

        return LiquidationState.NO_CHANGE

    def add_repay_borrow(self, sender, currency_code, amount, token_info_now, token_info_in_range):
        if self.address == sender:
            self.borrow_amounts.reduce_amount(currency_code, amount, token_info_now.get(currency_code))
            return self._get_liquidator_state(token_info_now, token_info_in_range)

        if self.lock_amounts.has_currency(currency_code) or self.borrow_amounts.has_currency(currency_code):
            return self._get_liquidator_state(token_info_now, token_info_in_range)

        return LiquidationState.NO_CHANGE

    def _get_liquidator_state(self, token_infos_now, token_infos_in_range):
        if token_infos_in_range is None:
            return LiquidationState.NO_CHANGE
        borrows = self.borrow_amounts.sum(token_infos_in_range)
        locks = self.lock_amounts.sum_can_borrow(token_infos_in_range)
        if borrows > locks:
            nb = self.borrow_amounts.sum(token_infos_now)
            nl = self.lock_amounts.sum_can_borrow(token_infos_now)
            if nb > nl:
                return LiquidationState.NOW
            return LiquidationState.IN_RANGE
        return LiquidationState.OUT_OF_RANGE

from violas_client.banktypes.bytecode import CodeType
from violas_client.vlstypes.view import TransactionView

class AccountsView():
    def __init__(self):
        self.accounts = dict()
        self.token_infos = dict()
        self.allow_liquidate = False

    def set_liquidate_state(self, allow_liquidate):
        self.liquidate = allow_liquidate
    
    def get(self, currency_code):
        return self.accounts.get(currency_code)
    
    def add_tx(self, tx:TransactionView):
        if not tx.is_successful():
            return
        token_infos_in_range = None
        if self.allow_liquidate:
            token_infos_in_range = self.get_token_infos()
        if tx.get_code_type() == CodeType.PUBLISH:
            return self.add_publish(tx)
        if tx.get_code_type() == CodeType.BORROW:
            return self.add_borrow(tx, self.token_infos, token_infos_in_range)
        if tx.get_code_type() == CodeType.LOCK:
            return self.add_lock(tx, self.token_infos, token_infos_in_range)
        if tx.get_code_type() == CodeType.REDEEM:
            return self.add_redeem(tx, self.token_infos, token_infos_in_range)
        if tx.get_code_type() == CodeType.REPAY_BORROW:
            return self.add_borrow(tx, self.token_infos, token_infos_in_range)
        if tx.get_code_type() == CodeType.REGISTER_TOKEN:
            return self.add_register_token(tx)
    
    def add_register_token(self, tx):
        event = tx.get_bank_event()
        currency_code = event.currency_code
        collateral_factor = event.collateral_factor
        base_rate = event.base_rate
        rate_multiplier = event.rate_multiplier
        rate_jump_multiplier = event.rate_jump_multiplier
        rate_kink = event.rate_kink
        token_info = TokenInfo.empty(currency_code, collateral_factor, rate_kink, rate_multiplier, base_rate, rate_jump_multiplier)
        self.token_infos[currency_code] = token_info
    
    def add_publish(self, tx):
        sender = tx.get_sender()
        self.accounts[sender] = AccountView.empty(sender)
    
    def add_borrow(self, tx, token_infos_now, token_infos_in_range):
        sender = tx.get_sender()
        currency_code = tx.get_currency_cde()
        amount = tx.get_amount()
        for ac in self.accounts:
            ac.add_borrow(sender, currency_code, amount, token_infos_now, token_infos_in_range)
    
    def add_lock(self, tx, token_infos_now, token_infos_in_range):
        for ac in self.accounts:
            ac.add_lock(tx, token_infos_now, token_infos_in_range)
    
    def add_redeem(self, tx, token_infos_now, token_infos_in_range):
        for ac in self.accounts:
            ac.add_redeem(tx, token_infos_now, token_infos_in_range)
    
    def add_repay_borrow(self, tx):
        pass

    def get_token_infos(self):
        pass

