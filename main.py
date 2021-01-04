from chain_client.client import Client as ChainClient
from violas_client import Client as ViolasClient
from account import get_account

account = get_account()
print(account.address_hex.upper())
# violas_client = ViolasClient("violas_testnet")
# print(violas_client.get_account_state(account.address_hex))
# chain_client = ChainClient()
# chain_client.mint_coin(account, "EUR", 1000)
# client = ViolasClient("violas_testnet")
# client = Client()
# client.mint_coin(account, "VLSEUR", 20_000_000)
