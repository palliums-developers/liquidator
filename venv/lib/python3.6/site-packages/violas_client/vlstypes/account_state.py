import copy
from extypes.account_state import AccountState as ExchangeAccountState
from banktypes.account_state import AccountState as BankAccountState

class AccountState(ExchangeAccountState, BankAccountState):
    @classmethod
    def new(cls, account_state):
        state = copy.deepcopy(account_state)
        state.__class__ = cls
        return state