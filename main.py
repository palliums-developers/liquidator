from bank import Bank, AccountView, TokenInfo
from bank.account import AccountLockAmounts, AccountBorrowAmounts
from network import create_database_manager, get_liquidator_account
#
# account = get_liquidator_account()
# print(account.address_hex)

data = "7b22666c6167223a202276696f6c6173222c202274797065223a202266756e6473222c20226f707474797065223a20226d6170222c2022636861696e223a202276696f6c6173222c20227472616e5f6964223a20223364323038643638313665343763666339396635616633616531326636343236222c2022746f6b656e5f6964223a2022564c53222c2022616d6f756e74223a20323030303030303030302c2022746f5f61646472657373223a202230786231346263333238366534623962343163383630323266326536313464373231222c20227374617465223a20227374617274227d"
print(bytes.fromhex(data))

# def test_keep_bank():
#     bank = Bank()
#     bank.update_from_db()
#     print(bank)
    # lock_amounts = AccountLockAmounts()
    # lock_amounts.amounts = {"lock_currency": 1}
    # borrow_amounts = AccountBorrowAmounts()
    # borrow_amounts.amounts = {"borrow_currency": 2}
    # bank.token_infos = {"tokens_infos": TokenInfo("token_code")}
    # bank.accounts = {"accounts": AccountView("addr", lock_amounts, borrow_amounts)}
    # bank.height = 100
    # bank.update_to_db()

# test_keep_bank()