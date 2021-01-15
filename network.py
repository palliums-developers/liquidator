import azure
from violas_client import Wallet
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from chain_client import Client as ChainClient
from http_client import Client as HttpClient
from testnet import *
from db import DBManager
from violas_client import Client as ViolasClient
from bank import Bank

os.environ["AZURE_CLIENT_ID"] = CLIENT_ID
os.environ["AZURE_TENANT_ID"] = TENANT_ID
os.environ["AZURE_CLIENT_SECRET"] = SECRET

def create_database_manager():
    return DBManager(dsn)

def create_http_client():
    return HttpClient(HTTP_SERVER)

def create_violas_client():
    return ViolasClient.new(CHAIN_URL)

def get_liquidator_account():
    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url=f"https://{VAULT_NAME}.vault.azure.net/", credential=credential)
    try:
        secret = secret_client.get_secret(LIQUIDATOR_SECRET_NAME).value
    except azure.core.exceptions.ResourceNotFoundError:
        wallet = Wallet.new()
        wallet.new_account()
        secret = wallet.mnemonic
        secret_client.set_secret(LIQUIDATOR_SECRET_NAME, secret)
    wallet = Wallet.new_from_mnemonic(secret)
    return wallet.new_account()

def mint_coin_to_liquidator_account(liquidator_account, currency_code, amount, currency_id=None):
    client = ChainClient(CHAIN_URL, DD_ADDR, HTTP_SERVER)
    return client.mint_coin(liquidator_account, currency_code, amount, currency_id)
