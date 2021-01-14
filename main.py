import time
import json
from violas_client import Wallet, Client
from bank import Bank, AccountView, TokenInfo
import time
from network import get_liquidator_account, create_http_client

wallet = Wallet.new()
a1 = wallet.new_account()

http_client = create_http_client()
http_client.try_create_child_vasp_account(a1)
client = Client("violas_testnet")
# currency_code = "vBTC"
account = get_liquidator_account()
client.transfer_coin(a1, account.address, 100)

