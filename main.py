from chain_client.client import Client as ChainClient
from violas_client import Client as ViolasClient
from account import get_account

versions = [1056000,
 1056018,
 1056034,
 1056050,
 1056068,
 1056085,
1056102,
1056114,
1056129,
1056150,
1056166,
1056183,
1056201,
1056216,
1056232,
1056250,
1056269,
1056300
            ]

from cache.api import liquidator_api

client = ViolasClient("violas_testnet")
for version in versions:
    tx = client.get_transaction(version)
    print(tx.get_code_type(), tx.get_version())
    liquidator_api.add_tx(tx)



# account = get_account()
# print(account.address_hex.upper())
# violas_client = ViolasClient("violas_testnet")
# print(violas_client.get_account_state(account.address_hex))
# chain_client = ChainClient()
# chain_client.mint_coin(account, "EUR", 1000)
# client = ViolasClient("violas_testnet")
# client = Client()
# client.mint_coin(account, "VLSEUR", 20_000_000)
