import os

BEI_JING_ADDR = "47.93.114.230"
AMERICA_EAST = "13.68.141.242"
LOCAL_HOST = "127.0.0.1"

HOST= BEI_JING_ADDR
PORT="5006"
USER="postgres"
PASSWORD="liquidator-postgres"
DATABASE="postgres"

dsn = f"postgres://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

CLIENT_ID = "90f023f9-82b6-4b93-beb6-561743f9af84"
TENANT_ID = "d99eee11-8587-4c34-9201-38d5247df9c9"
SECRET = "eRvgvZxMh_v27EWR5-Z-C2DWo~yc_78jfR"
VAULT_NAME = "violas-test-liquidator"
LIQUIDATOR_SECRET_NAME = "liquidator-secret"

os.environ["AZURE_CLIENT_ID"] = CLIENT_ID
os.environ["AZURE_TENANT_ID"] = TENANT_ID
os.environ["AZURE_CLIENT_SECRET"] = SECRET


CHAIN_URL = f"http://{HOST}:50001"
DD_ADDR = "00000000000000000042524746554e44"

HTTP_SERVER="https://api4.violas.io/1.0/violas/mint"

DEFAULT_COIN_NAME = "VLS"
