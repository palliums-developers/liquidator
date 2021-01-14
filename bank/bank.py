import dataclasses
from typing import Dict
from .base import Base
from .token_info import TokenInfo
from .account import AccountView
from .util import mantissa_mul, mantissa_div, new_mantissa
from violas_client.banktypes.bytecode import CodeType as BankCodeType
from violas_client.vlstypes.view import TransactionView
from violas_client.oracle_client.bytecodes import CodeType as OracleCodType
from network import create_database_manager

@dataclasses.dataclass(init=False)
class Bank(Base):
    _instance = None


    height: int
    accounts: Dict[str, AccountView]
    token_infos: Dict[str, TokenInfo]

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "height"):
            self.handers = {
                BankCodeType.BORROW2: self.add_borrow,
                BankCodeType.BORROW_INDEX: self.add_borrow,
                BankCodeType.BORROW: self.add_borrow,
                BankCodeType.CLAIM_INCENTIVE: None,
                BankCodeType.CREATE_TOKEN: None,
                BankCodeType.DISABLE: None,
                BankCodeType.ENTER_BANK: None,
                BankCodeType.EXIT_BANK: None,
                BankCodeType.LIQUIDATE_BORROW_INDEX: self.add_liquidate_borrow,
                BankCodeType.LIQUIDATE_BORROW: self.add_liquidate_borrow,
                BankCodeType.LOCK2: self.add_lock,
                BankCodeType.LOCK_INDEX: self.add_lock,
                BankCodeType.LOCK: self.add_lock,
                BankCodeType.MIGRATE: None,
                BankCodeType.MINT: None,
                BankCodeType.PUBLISH: self.add_publish,
                BankCodeType.REDEEM2: self.add_redeem,
                BankCodeType.REDEEM_INDEX: self.add_redeem,
                BankCodeType.REDEEM: self.add_redeem,
                BankCodeType.REGISTER_LIBRA_TOKEN: self.add_register_libra_token,
                BankCodeType.REPAY_BORROW2: self.add_repay_borrow,
                BankCodeType.REPAY_BORROW_INDEX: self.add_repay_borrow,
                BankCodeType.REPAY_BORROW: self.add_repay_borrow,
                BankCodeType.SET_INCENTIVE_RATE2: None,
                BankCodeType.SET_INCENTIVE_RATE: None,
                BankCodeType.TEST: None,
                BankCodeType.UPDATE_PRICE_FROM_ORACLE: self.update_price_from_oracle,
                BankCodeType.UPDATE_PRICE_INDEX: None,
                BankCodeType.UPDATE_PRICE: self.update_price,
                BankCodeType.UPDATE_COLLATERAL_FACTOR: self.update_collateral_factor,
                BankCodeType.UPDATE_RATE_MODEL: self.update_rate_model,
                OracleCodType.UPDATE_EXCHANGE_RATE: self.update_oracle_price
            }

            self.height = 0
            self.accounts = {}
            self.token_infos = {}
            self.modified_accounts = {}

    def get_token_info(self, currency_code) -> TokenInfo:
        return self.token_infos.get(currency_code)

    def get_account(self, addr) -> AccountView:
        account = self.accounts.get(addr)
        if account is None:
            account = AccountView(addr)
            self.accounts[addr] = account
        self.modified_accounts[addr] = account
        return account

    def get_accounts_of_state(self, max_health):
        return filter(lambda account: account.health <= max_health, self.accounts.values())

    def get_accounts_has_borrow(self):
        return filter(lambda account: account.has_borrow_any(), self.accounts.values())

    def get_accounts_has_borrow_and_lock_specificed_currency(self, currency_code):
        '''
        汇率降低时需要更新的账户(汇率升高时虽然有该存款的会升高， 但是不是实时的，只有在下一分钟才会生效)
            有借款且存款有该币种的
        '''
        return filter(lambda account: account.has_borrow_any() and account.has_lock(currency_code), self.accounts.values())

    def add_tx(self, tx: TransactionView):
        if not tx.is_successful():
            return
        code_type = tx.get_code_type()
        hander = self.handers.get(code_type)
        if hander is not None:
            try:
                token_info = self.get_token_info("vBTC")
                print(token_info.last_minute)
            except:
                pass
            hander(tx)

    def add_publish(self, tx):
        '''
        添加一个账户
        '''
        self.accounts[tx.get_sender()] = AccountView(tx.get_sender())
        self.modified_accounts[tx.get_sender()] = self.accounts[tx.get_sender()]

    def add_register_libra_token(self, tx):
        events = tx.get_bank_type_events(BankCodeType.REGISTER_LIBRA_TOKEN)
        if len(events) > 0:
            event = events[0].get_bank_event()
            self.token_infos[event.currency_code] = TokenInfo.empty(
                oracle_price=self.get_oracle_price(event.currency_code),
                currency_code=event.currency_code,
                collateral_factor=event.collateral_factor,
                base_rate=event.base_rate//(365*24*60),
                rate_multiplier=event.rate_multiplier//(365*24*60),
                rate_jump_multiplier=event.rate_jump_multiplier//(365*24*60),
                rate_kink=event.rate_kink,
                last_minute=events[0].get_timestamp() // 60)

    def add_borrow(self, tx):
        '''
        1. 更新oracle价格
        2. accrue_interest
        3. 更新账户的数据
            借款人账户的数据
        '''
        ret = []
        timestamps = tx.get_bank_timestamp()
        currency_code = tx.get_currency_code()
        token_info = self.get_token_info(currency_code)
        price = self.get_price(currency_code)
        oracle_price = self.get_oracle_price(currency_code)
        if price != oracle_price:
            self.set_price(currency_code, oracle_price)
            price = oracle_price
        token_info.accrue_interest(timestamps)
        token_info.add_borrow(tx)
        account = self.get_account(tx.get_sender())
        if account.add_borrow(currency_code, tx.get_amount(), self.token_infos) < 1:
            ret.append(account.address)
        if oracle_price is not None and price > oracle_price:
            accounts = self.get_accounts_has_borrow_and_lock_specificed_currency(currency_code)
            for account in accounts:
                if account.address == tx.get_sender():
                    continue
                if account.update_health_state(self.token_infos) < 1:
                    ret.append(account.address)
        return ret


    def add_lock(self, tx):
        '''
        1. 更新oracle价格
        2. accrue_interest
        3. 更新账户数据
            存款人账户的数据
        4. 更新token_info
        '''
        ret = []
        timestamps = tx.get_bank_timestamp()
        currency_code = tx.get_currency_code()
        token_info = self.get_token_info(currency_code)
        price = self.get_price(currency_code)
        oracle_price = self.get_oracle_price(currency_code)
        if price != oracle_price:
            self.set_price(currency_code, oracle_price)
            price = oracle_price
        token_info.accrue_interest(timestamps)
        token_info.update_exchange_rate()
        account = self.get_account(tx.get_sender())
        if account.add_lock(currency_code, tx.get_amount(), self.token_infos) < 1:
            ret.append(account.address)
        token_info.add_lock(tx)
        if oracle_price is not None and price > oracle_price:
            accounts = self.get_accounts_has_borrow_and_lock_specificed_currency(currency_code)
            for account in accounts:
                if account.address == tx.get_sender():
                    continue
                if account.update_health_state(self.token_infos) < 1:
                    ret.append(account.address)
        return ret

    def add_redeem(self, tx):
        '''
        1. 更新oralce价格
        2. accrue_interest
        3. 更新账户数据
            取款人的数据
        4. 更新token_info
        '''
        ret = []
        timestamps = tx.get_bank_timestamp()
        currency_code = tx.get_currency_code()
        token_info = self.get_token_info(currency_code)
        price = self.get_price(currency_code)
        oracle_price = self.get_oracle_price(currency_code)
        if price != oracle_price:
            self.set_price(currency_code, oracle_price)
            price = oracle_price
        token_info.accrue_interest(timestamps)
        token_info.update_exchange_rate()

        token_info.add_redeem(tx)
        account = self.get_account(tx.get_sender())
        if account.add_redeem(currency_code, tx.get_amount(), self.token_infos) < 1:
            ret.append(account.address)
        if oracle_price is not None and price > oracle_price:
            accounts = self.get_accounts_has_borrow_and_lock_specificed_currency(currency_code)
            for account in accounts:
                if account.address == tx.get_sender():
                    continue
                if account.update_health_state(self.token_infos) < 1:
                    ret.append(account.address)
        return ret

    def add_repay_borrow(self, tx):
        '''
        1. 更新oralce价格
        2. accrue_interest
        3. 更新账户数据
            还款人的数据
        '''
        ret = []
        timestamps = tx.get_bank_timestamp()
        currency_code = tx.get_currency_code()
        token_info = self.get_token_info(currency_code)
        price = self.get_price(currency_code)
        oracle_price = self.get_oracle_price(currency_code)
        if price != oracle_price:
            self.set_price(currency_code, oracle_price)
            price = oracle_price

        token_info.accrue_interest(timestamps)
        account = self.get_account(tx.get_sender())
        if account.add_repay_borrow(currency_code, tx.get_amount(), self.token_infos) < 1:
            ret.append(account.address)
        token_info.add_repay_borrow(tx)
        if oracle_price is not None and price > oracle_price:
            accounts = self.get_accounts_has_borrow_and_lock_specificed_currency(currency_code)
            for account in accounts:
                if account.address == tx.get_sender():
                    continue
                if account.update_health_state(self.token_infos) < 1:
                    ret.append(account.address)
        return ret

    def add_liquidate_borrow(self, tx: TransactionView):
        '''
        1. 质押币总额不变
        2. 借款纵隔
        '''
        ret = []
        timestamps = tx.get_bank_timestamp()
        currency_code = tx.get_currency_code()
        collateral_currency = tx.get_collateral_currency()
        token_info = self.get_token_info(currency_code)
        price = self.get_price(currency_code)
        oracle_price = self.get_oracle_price(currency_code)
        if price != oracle_price:
            self.set_price(currency_code, oracle_price)
            price = oracle_price
        collateral_token_info = self.get_token_info(collateral_currency)
        collateral_price = self.get_price(collateral_currency)
        collateral_oracle_price = self.get_oracle_price(collateral_currency)
        if collateral_price != collateral_oracle_price:
            self.set_price(collateral_currency, collateral_oracle_price)

        token_info.accrue_interest(timestamps)

        token_info.add_liquidate_borrow(tx)
        amount = tx.get_amount()
        value = mantissa_mul(amount, price)
        value = mantissa_div(value, collateral_token_info.update_exchange_rate())
        value = mantissa_div(value, collateral_price)
        value += mantissa_mul(value, new_mantissa(1, 10))

        account = self.get_account(tx.get_sender())
        borrower = self.get_account(tx.get_borrower())

        if account.add_liquidate_borrow_to_liquidator(collateral_currency, value, self.token_infos) < 1:
            ret.append(account.address)
        if borrower.add_liquidate_borrow_to_borrower(collateral_currency, value, currency_code, tx.get_amount(), self.token_infos) < 1:
            ret.append(account.address)

        if oracle_price is not None and price > oracle_price:
            accounts = self.get_accounts_has_borrow_and_lock_specificed_currency(currency_code)
            for account in accounts:
                if account.address == tx.get_sender():
                    continue
                if account.update_health_state(self.token_infos) < 1:
                    ret.append(account.address)

        if collateral_price > collateral_oracle_price:
            accounts = self.get_accounts_has_borrow_and_lock_specificed_currency(collateral_currency)
            for account in accounts:
                if account.address == tx.get_sender():
                    continue
                if account.update_health_state(self.token_infos) < 1:
                    ret.append(account.address)
        return ret

    def update_collateral_factor(self, tx):
        '''
        1. 更新token_info
        2. 更新账户数据
            变大则更新有lock且有贷款的
        '''
        ret = []
        events = tx.get_bank_type_events(BankCodeType.UPDATE_COLLATERAL_FACTOR)
        event = events[0]
        factor = event.get_factor()
        currency_code = event.get_currency_code()
        token_info = self.get_token_info(currency_code)
        pro_factor = token_info.collateral_factor
        token_info.collateral_factor = factor
        if pro_factor < factor:
            accounts = self.get_accounts_has_borrow_and_lock_specificed_currency(currency_code)
            for account in accounts:
                health = account.update_health_state(token_info)
                if health < 1:
                    ret.append(account.address)
        return ret

    def update_price_from_oracle(self, tx):
        '''
        1. 更新本地价格
        2. 更新账户信息
        '''
        ret = []
        currency_code = tx.get_currency_code()
        price = self.get_price(currency_code)
        oracle_price = self.get_oracle_price(currency_code)
        if price != oracle_price:
            self.set_price(currency_code, oracle_price)
            price = oracle_price
        if oracle_price is not None and price > oracle_price:
            accounts = self.get_accounts_has_borrow_and_lock_specificed_currency(currency_code)
            for account in accounts:
                if account.address == tx.get_sender():
                    continue
                if account.update_health_state(self.token_infos) < 1:
                    ret.append(account.address)
        return ret

    def update_price(self, tx):
        self.set_price(tx.get_currency_code(), tx.get_price())

    def update_oracle_price(self, tx):
        price = tx.get_oracle_event().get_value()
        if price is not None:
            return self.set_oracle_price(tx.get_currency_code(), price)

    def update_rate_model(self, tx: TransactionView):
        events = tx.get_bank_type_events(BankCodeType.UPDATE_RATE_MODEL)
        if len(events) > 0:
            event = events[0].get_bank_event()
            token_info = self.token_infos[event.currency_code]
            token_info.base_rate = event.base_rate //(365*24*60)
            token_info.rate_multiplier = event.rate_multiplier // (365*24*60)
            token_info.rate_jump_multiplier = event.rate_jump_multiplier // (365*24*60)
            token_info.rate_kink = event.rate_kink

    def check_borrow_index(self, time_minute):
        ret = []
        cur_token_infos = dict()
        for currency_code, token_info in self.token_infos.items():
            cur_token_infos[currency_code] = token_info.get_forecast(time_minute)

        for account in self.get_accounts_has_borrow():
            health = account.update_health_state(cur_token_infos)
            if health < 1:
                ret.append(account.address)
        return ret

    def get_price(self, currency_code):
        token_info = self.get_token_info(currency_code)
        if token_info:
            return token_info.price

    def set_price(self, currency_code, price):
        token_info = self.get_token_info(currency_code)
        if token_info and price != 0:
            token_info.price = price

    def get_oracle_price(self, currency_code):
        token_info = self.get_token_info(currency_code)
        if token_info:
            return token_info.oracle_price

    def set_oracle_price(self, currency_code, price):
        token_info = self.get_token_info(currency_code)
        if token_info:
            token_info.oracle_price = price
        else:
            token = TokenInfo(currency_code=currency_code, oracle_price=price)
            self.token_infos[currency_code] = token

    def update_to_db(self):
        db_manage = create_database_manager()
        db_manage.sets(self.modified_accounts)
        # for k, v in self.modified_accounts.items():
        #     db_manage.set(k, v)
        for k, v in self.token_infos.items():
            db_manage.set(k, v)
        db_manage.set("height", self.height)

    def update_from_db(self):
        db_manage = create_database_manager()
        accounts = db_manage.gets(AccountView)
        tokens = db_manage.gets(TokenInfo)
        for account in accounts:
            self.accounts[account.address] = account
        for token in tokens:
            self.token_infos[token.currency_code] = token
        self.height = db_manage.get("height", int, 0)
        # print(self.accounts["6c1dd50f35f120061babc2814cf9378b"].borrow_amounts, type(self.accounts["6c1dd50f35f120061babc2814cf9378b"].borrow_amounts))

