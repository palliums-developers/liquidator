from violas_client import Client
from bank import Bank
import copy
from network import get_liquidator_account


client = Client("violas_testnet")
addr = "84ef3d263b3b19f7bc957a389c44d208"

account = get_liquidator_account()
client.bank_liquidate_borrow(account, addr, "vBTC", "vBTC", 634)
# print(client.bank_get_total_collateral_value(addr))
# print(client.bank_get_total_borrow_value(addr))


