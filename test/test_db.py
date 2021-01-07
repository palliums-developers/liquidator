from db import DBManager
from bank import Bank, AccountView, TokenInfo
from bank.account import AccountLockAmounts, AccountBorrowAmounts
from network import create_database_manager

def test_db():
    bank = Bank()
    account_view = AccountView("addr")
    bank.accounts = {"accounts": account_view}
    bank.token_infos = {"token_infos": TokenInfo("token_info")}
    db_manage = create_database_manager()
    db_manage.set("bank", bank)
    print(db_manage.get())