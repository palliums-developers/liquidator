from violas_client import Client


client = Client("violas_testnet")
state = client.get_account_state(client.BANK_MODULE_ADDRESS, 635500)
print(state)
# print(state.get_token_info_store_resource(False))
