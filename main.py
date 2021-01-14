import time
import json
from violas_client import Wallet, Client
from bank import Bank, AccountView, TokenInfo
import time

client = Client("violas_testnet")
currency_code = "vBTC"

index = client.bank_get_currency_index(currency_code)
token_info = client.get_account_state(client.BANK_OWNER_ADDRESS).get_tokens_resource()
print(token_info)

