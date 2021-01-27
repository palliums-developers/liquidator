from violas_client import Client


client = Client("violas_testnet")
state = client.get_account_state(client.get_account_state())
print(state.get_tokens_resource())
