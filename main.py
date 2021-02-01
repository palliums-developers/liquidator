from violas_client import Client
from bank import Bank
import copy
from network import get_liquidator_account


client = Client("violas_testnet")
addr = "fae3a86a20a72aa1a4bb93efa79a7bac"

# account = get_liquidator_account()
# client.bank_liquidate_borrow(account, addr, "vBTC", "vBTC", 276)
print(client.bank_get_total_collateral_value(addr))
print(client.bank_get_total_borrow_value(addr))


