from network import create_violas_client
from violas_client import Wallet, Client

currency_code = "USD"
client = Client()
wallet = Wallet.new()
a1 = wallet.new_account()
client.mint_coin(a1.address, 50_000_000, auth_key_prefix=a1.auth_key_prefix, currency_code=currency_code)
seq = client.bank_publish(a1)
print(client.bank_get_amount(client.BANK_OWNER_ADDRESS, currency_code))
seq = client.bank_enter(a1, 10_000_000, currency_code=currency_code)
print(client.bank_get_amount(client.BANK_OWNER_ADDRESS, currency_code))

