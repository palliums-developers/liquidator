import os
import azure
from violas_client import Wallet
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

CLIENT_ID = "90f023f9-82b6-4b93-beb6-561743f9af84"
TENANT_ID = "d99eee11-8587-4c34-9201-38d5247df9c9"
SECRET = "eRvgvZxMh_v27EWR5-Z-C2DWo~yc_78jfR"
VAULT_NAME = "violas-test-liquidator"
LIQUIDATOR_SECRET_NAME = "liquidator-secret"

os.environ["AZURE_CLIENT_ID"] = CLIENT_ID
os.environ["AZURE_TENANT_ID"] = TENANT_ID
os.environ["AZURE_CLIENT_SECRET"] = SECRET

def get_account():
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

if __name__ == "__main__":
    account = get_account()
    print(account.address_hex)

