from violas_client import Client
from bank import Bank
import copy


# client = Client("violas_testnet")
# state = client.get_account_state(client.get_account_state())
# print(state.get_tokens_resource())


bank = Bank()
token_info = copy.deepcopy(bank.token_infos)
token_info["token"] = "info"
print(bank.token_infos)
print(token_info)
