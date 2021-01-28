from violas_client import Client
from bank import Bank
import copy


client = Client("violas_testnet")
state = client.get_account_state("8ac60db3f51254ab93665f26f1349828")
print(state.get_tokens_resource())

