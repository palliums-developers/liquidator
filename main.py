import time
from cache.api import liquidator_api
from violas_client import Client, Wallet

client = Client("bj_testnet")
bank_addr = client.BANK_OWNER_ADDRESS
oracle_addr = client.ORACLE_OWNER_ADDRESS

print(client.get_account_transaction(bank_addr, 0).get_version())

