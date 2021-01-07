from bank import Bank, AccountView, TokenInfo
from bank.account import AccountLockAmounts, AccountBorrowAmounts
from network import create_database_manager

def test_keep_bank():
    bank = Bank()
    bank.update_from_db()
    print(bank)
    # lock_amounts = AccountLockAmounts()
    # lock_amounts.amounts = {"lock_currency": 1}
    # borrow_amounts = AccountBorrowAmounts()
    # borrow_amounts.amounts = {"borrow_currency": 2}
    # bank.token_infos = {"tokens_infos": TokenInfo("token_code")}
    # bank.accounts = {"accounts": AccountView("addr", lock_amounts, borrow_amounts)}
    # bank.height = 100
    # bank.update_to_db()

test_keep_bank()