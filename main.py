import time
import json
from violas_client import Wallet, Client
from bank import Bank, AccountView, TokenInfo
import time
from network import get_liquidator_account, create_http_client

wallet = Wallet.new()
a1 = wallet.new_account()

client = Client("violas_testnet")
state = client.get_account_state(client.BANK_OWNER_ADDRESS)
print(state)

