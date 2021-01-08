from bank import Bank, AccountView, TokenInfo
from bank.account import AccountLockAmounts, AccountBorrowAmounts
from network import create_database_manager, get_liquidator_account, create_violas_client

client = create_violas_client()
client.add_currency_to_account(get_liquidator_account(), "vBTC")
print(get_liquidator_account().address_hex)

