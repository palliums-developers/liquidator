import time
import json
from violas_client import Wallet, Client
from bank import Bank, AccountView, TokenInfo
import time
from network import get_liquidator_account, create_http_client

account = get_liquidator_account()
client = Client("violas_testnet")
client.mint_coin(account.address_hex, 2_000_000_000, currency_code="vUSDT")

# client.mint_coin(account.address_hex, 5_000_000_000, currency_code="vBTC")
# client.bank_enter(account, 2_000_000_000, currency_code="vBTC")