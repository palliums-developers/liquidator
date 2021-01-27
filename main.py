from violas_client import Client
from bank import Bank
import copy


client = Client("violas_testnet")
state = client.get_account_state(client.BANK_OWNER_ADDRESS, 12481870)
print(state.get_token_info_store_resource(accrue_interest=False))

