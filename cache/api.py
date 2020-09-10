import time
from .token_info import TokenInfo
from .account import AccountView
from violas_client.banktypes.bytecode import CodeType as BankCodeType
from violas_client.lbrtypes.bytecode import CodeType as LibraCodeType
from violas_client.vlstypes.view import TransactionView
from violas_client.oracle_client.bytecodes import CodeType as OracleCodType

class LiquidatorAPI():
    def __init__(self):
        self.accounts = dict()
        self.token_infos = dict()
        self.compound_prices = dict()
        self.token_prices = dict()

    def get_token_info(self, currency_code) -> TokenInfo:
        return self.token_infos.get(currency_code)

    def get_account(self, addr) -> AccountView:
        return self.accounts.get(addr)

    def get_accounts_of_state(self, max_health):
        return filter(lambda account: account.health <= max_health, self.accounts.values())

    def get_accounts_when_depreciation(self, currency_code):
        '''
        汇率降低时需要更新的账户
            有借款且存款有该币种的
        '''
        return filter(lambda account: account.has_borrow_any() and account.has_lock(currency_code), self.accounts.values())

    def add_tx(self, tx: TransactionView):
        if not tx.is_successful():
            return
        if tx.get_code_type() == BankCodeType.BORROW:
            return self.add_borrow(tx)
        if tx.get_code_type() == BankCodeType.LOCK:
            return self.add_lock(tx)
        if tx.get_code_type() == BankCodeType.REDEEM:
            return self.add_redeem(tx)
        if tx.get_code_type() == BankCodeType.REPAY_BORROW:
            return self.add_borrow(tx)
        if tx.get_code_type() == BankCodeType.UPDATE_PRICE:
            pass
        if tx.get_code_type() == BankCodeType.UPDATE_EXCHANGE_RATE:
            pass

    def add_borrow(self, tx):
        '''
        1. 更新oracle价格
        2. accrue_interest
        3. 更新token_info的数据
        4. 更新账户的数据
            借款人账户的数据
            所有拥有该币存款的账户数据（exchangeRate = (totalCash + totalBorrows - totalReserves) / totalSupply）, 影响borrow_rate, 但是不影响borrow_index
        '''
        currency_code = tx.get_currency_code()
        token_info = self.get_token_info(currency_code)
        price = self.get_price(currency_code)
        oracle_price = self.get_oracle_price(currency_code)
        if price != oracle_price:
            self.set_price(oracle_price)
        token_info.accrue_interest()
        account = self.get_account(tx.get_sender())
        health = account.add_borrow(currency_code, self.token_infos)
        if health < 1:
            self.liquidate_borrow()

        if price > oracle_price:
            accounts = self.get_accounts_when_depreciation(currency_code)
            for account in accounts:
                pass
        pass

    def add_lock(self, tx):
        pass

    def add_redeem(self, tx):
        pass

    def update_price_from_oracle(self, currency):
        pass


    def get_price(self, currency_code):
        token_info = self.get_token_info(currency_code)
        if token_info:
            return token_info.price

    def set_price(self, currency_code, price):
        token_info = self.get_token_info(currency_code)
        if token_info:
            token_info.price = price

    def get_oracle_price(self, currency_code):
        token_info = self.get_token_info(currency_code)
        if token_info:
            return token_info.oracle_price

    def set_oracle_price(self, currency_code, price):
        token_info = self.get_token_info(currency_code)
        if token_info:
            token_info.oracle_price = price

    def liquidate_borrow(self):
        pass




    # def add_tx(self, tx: TransactionView):
    #     if not tx.is_successful():
    #         return
    #     if tx.get_code_type() == CodeType.BORROW:
    #         return self.add_borrow(tx)
    #     if tx.get_code_type() == CodeType.LOCK:
    #         return self.add_lock(tx)
    #     if tx.get_code_type() == CodeType.REDEEM:
    #         return self.add_redeem(tx)
    #     if tx.get_code_type() == CodeType.REPAY_BORROW:
    #         return self.add_borrow(tx)
    #     if tx.get_code_type() == CodeType.UPDATE_PRICE:
    #         pass
    #     if tx.get_code_type() == OracleCodeType.UPDATE_EXCHANGE_RATE:
    #         pass
    #
    # def set_account_state(self, account_address, state):
    #     if state is not None and account_address is not None:
    #         pro_state = self.get_account_state(account_address)
    #         if pro_state is not None:
    #             self.state_accounts.get(pro_state).remove(account_address)
    #         self.accounts[account_address].set_account_state = state
    #         self.state_accounts.get(state).add(account_address)
    #
    # def add_publish(self, tx):
    #     sender = tx.get_sender()
    #     self.accounts[sender] = AccountView.empty(sender)
    #
    # def add_borrow(self, tx, token_infos):
    #     sender = tx.get_sender()
    #     currency_code = tx.get_currency_cde()
    #     amount = tx.get_amount()
    #     for ac in self.accounts:
    #         ac.add_borrow(sender, currency_code, amount, token_infos)
    #
    # def add_lock(self, tx, token_infos):
    #     for ac in self.accounts:
    #         ac.add_lock(tx, token_infos)
    #
    # def add_redeem(self, tx, token_infos):
    #     for ac in self.accounts:
    #         ac.add_redeem(tx, token_infos)
    #
    # def add_repay_borrow(self, tx, token_infos):
    #     for ac in self.accounts:
    #         ac.add_repay_borrow(tx, token_infos)
    #
    # def add_liquidate_borrow(self, tx, token_infos):
    #     liquidator = self.accounts.get(tx.get_sender())
    #     borrower = self.accounts.get(tx.get_borrower())
    #     liquidator.add_liquidate_borrow_to_liquidator(tx.get_sender(), tx.get_collateral_currency_code(),
    #                                                   tx.get_collateral_amount(), token_infos)
    #     borrower.add_liquidate_borrow_to_borrower(tx.get_borrower(), tx.get_collateral_currency_code(),
    #                                               tx.get_collateral_amount(),
    #                                               tx.get_currency_code(), tx.get_amount(),
    #                                               token_infos)
    #
    # def update_liquidation_state(self, token_infos):
    #     for pro_state, addr in self.state_accounts:
    #         account = self.accounts.get(addr)
    #         cur_state = account.get_liquidator_state(token_infos)
    #         if cur_state != pro_state:
    #             self.set_account_state(addr, cur_state)
    #
    # def get_token_info(self, currency_code) -> TokenInfo:
    #     return self.token_infos.get(currency_code)
    #
    # def add_borrow(self, tx):
    #     currency_code = tx.get_currency_cde()
    #     token_info = self.get_token_info(currency_code)
    #     if token_info is not None:
    #         pass
    #     token_info.add_borrow(tx)
    #
    # def add_lock(self, tx):
    #     currency_code = tx.get_currency_cde()
    #     token_info = self.get_token_info(currency_code)
    #     if token_info is not None:
    #         token_info.add_lock(tx)
    #
    # def add_redeem(self, tx):
    #     currency_code = tx.get_currency_cde()
    #     token_info = self.get_token_info(currency_code)
    #     if token_info is not None:
    #         token_info.accrue_interest()
    #
    # def add_register_token(self, tx):
    #     event = tx.get_bank_event()
    #     currency_code = event.currency_code
    #     collateral_factor = event.collateral_factor
    #     base_rate = event.base_rate
    #     rate_multiplier = event.rate_multiplier
    #     rate_jump_multiplier = event.rate_jump_multiplier
    #     rate_kink = event.rate_kink
    #     token_info = TokenInfo.empty(currency_code=currency_code,
    #                                  owner=tx.get_sender(),
    #                                  collateral_factor=collateral_factor,
    #                                  base_rate=base_rate,
    #                                  rate_multiplier=rate_multiplier,
    #                                  rate_jump_multiplier=rate_jump_multiplier,
    #                                  rate_kink=rate_kink,
    #                                  bulletin_first="",
    #                                  bulletins="")
    #
    #     self.token_infos[currency_code] = token_info
    #
    # def get_token_infos_a_minute_later(self):
    #     ret = []
    #     minu_later_time = time.time() + 60
    #     for token_info in self.token_infos:
    #         ret.append(token_info.get_forecast(minu_later_time))
    #     return ret
    #
    # def get_forecast_token_infos(self, t):
    #     ret = []
    #     for token_info in self.token_infos:
    #         ret.append(token_info.get_forecast(t))
    #     return ret


liquidator_api = LiquidatorAPI()