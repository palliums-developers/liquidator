import time
import json
from violas_client import Wallet, Client
from bank import Bank, AccountView, TokenInfo
import time
from network import get_liquidator_account, create_http_client

account = get_liquidator_account()
# print(account.address_hex)
client = Client("violas_testnet")
client.mint_coin(account.address_hex, 3_000_000_000, currency_code="vBTC")
# print(client.bank_get_amounts(account.address_hex))
# addr = "3F36F03FE6CAA661AE4EA1F8B55BA906"
# b = client.bank_get_total_borrow_value(addr)
# l = client.bank_get_total_collateral_value(addr)
# print(b-l)
# client.mint_coin(account.address_hex, 2_000_000_000, currency_code="vUSDT")

# client.mint_coin(account.address_hex, 5_000_000_000, currency_code="vBTC")
# client.bank_enter(account, 2_000_000_000, currency_code="vBTC")