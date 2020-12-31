from chain_client.client import Client
from violas_client import Client as ViolasClient

account = get_account()
client = ViolasClient("violas_testnet")
client = Client()
client.mint_coin(account, "VLSEUR", 20_000_000)
