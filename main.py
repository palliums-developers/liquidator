from violas_client import Client
from bank import Bank
import copy
from network import get_liquidator_account


client = Client("violas_testnet")
addr = "0003d51002e8aaaa8e9016fbb3d11165"

# account = get_liquidator_account()
# client.bank_liquidate_borrow(account, addr, "vBTC", "vBTC", 276)
print(client.bank_get_total_collateral_value(addr))
print(client.bank_get_total_borrow_value(addr))


