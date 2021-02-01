from violas_client import Client
from bank import Bank
from bank.util import mantissa_mul
import copy
from network import get_liquidator_account
v1 = mantissa_mul(mantissa_mul(279779638216, 2147483647), 147710732832604)
v2 = mantissa_mul(mantissa_mul(626566987229, 2147483647), 4294967296)
print(v1+ v2)


# client = Client("violas_testnet")
# addr = "9eda02e6161f9268e9d78c739b8ae777"
# state = client.get_account_state(addr)
# print(state.get_tokens_resource())

# account = get_liquidator_account()
# client.bank_liquidate_borrow(account, addr, "vBTC", "vBTC", 634)
# print(client.bank_get_total_collateral_value(addr) - client.bank_get_total_borrow_value(addr))
# print(client.bank_get_total_borrow_value(addr))


