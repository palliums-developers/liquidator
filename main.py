from violas_client import Client


client = Client("violas_testnet")
state = client.get_account_state("2a99d1954c1fdd527aca504844326005")
print(state.get_tokens_resource())
