import time
from .account import AccountsView, LiquidationState
from .token_info import TokenInfos
from violas_client.banktypes.bytecode import CodeType
from violas_client.lbrtypes.bytecode import CodeType as LibraCodeType

class LiquidatorAPI():
    def __init__(self):
        self.accounts_view = AccountsView()
        self.token_infos = TokenInfos()
        self.last_update_minute = 0
        self.update_state = False

    def add_tx(self, tx):
        code_type = tx.get_code_type()
        if code_type != LibraCodeType.BLOCK_METADATA and code_type in CodeType:
            self.token_infos.add_tx(tx)
            self.accounts_view.add_tx(tx)
            return self.get_accounts_of_liquidation_state(LiquidationState.EXPIRED)

    def get_accounts_of_liquidation_state(self, liquidation_state):
        return self.accounts_view.get_account_state(liquidation_state)

    def get_ctoken_info(self, currency_code):
        return self.token_infos.get_token_info(currency_code)

    def update_accounts_liquidation_state(self):
        cur_time = time.time()
        if self.update_state is True and cur_time // 60 > self.last_update_minute:
            token_infos = self.token_infos.get_forecast_token_infos(cur_time)
            self.accounts_view.update_liquidation_state(token_infos)

liquidator_api = LiquidatorAPI()