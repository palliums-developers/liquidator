import time
import json
from violas_client import Wallet, Client
from bank import Bank, AccountView, TokenInfo
import time
from network import get_liquidator_account, create_http_client
from bank.bank import Bank


addr= get_liquidator_account().address_hex
# bank = Bank()
# bank.update_from_db()
# print(bank.to_json())

client = Client("violas_testnet")
print(client.get_account_transaction(addr, 0).get_version())
# state =client.get_account_state(client.BANK_OWNER_ADDRESS)
# print(state.get_token_info_store_resource(accrue_interest = False))
# print(state.get_tokens_resource())
