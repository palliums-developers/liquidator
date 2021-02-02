from violas_client import Client
from bank import Bank
from bank.util import mantissa_mul
import copy
from network import get_liquidator_account



client = Client("violas_testnet")
addr = "957f949ca46db1640dd16b50797e82b8"
# state = client.get_account_state(addr)
# print(state.get_tokens_resource())

account = get_liquidator_account()
client.bank_liquidate_borrow(account, addr, "vBTC", "vBTC", 634)
# print(client.bank_get_total_collateral_value(addr) - client.bank_get_total_borrow_value(addr))
# print(client.bank_get_total_borrow_value(addr))


