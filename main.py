from violas_client import Client


client = Client("violas_testnet")
state = client.get_account_state(client.BANK_OWNER_ADDRESS)
print(state.get_token_info_store_resource(False))
