from violas_client import Client
from cache.api import liquidator_api



client = Client("bj_testnet")
token_infos = client.get_account_state(client.get_bank_owner_address()).get_token_info_store_resource()
print(token_infos)

# addrs = [client.BANK_OWNER_ADDRESS, "008e290b2104836059b2470b3d7b5a27", "1e0551a1a703f3c47e80ad5dddcbfc5b", "4ac2f93734a4aee8cb907d14dc39a055", "54c9b693169248731486981145613fb2", "e3ca00025d84d129cf9643aff3e7085e", "fec9e6e216105d40132e368c7046ed1c"]
# txs = []
# for addr in addrs:
#     seq = client.get_sequence_number(addr)
#     for i in range(seq):
#         tx = client.get_account_transaction(addr, i)
#         txs.append(tx)
# txs.sort(key = lambda tx: tx.get_version())
# liquidator_api.set_oracle_price("USD", 4294967296)
# liquidator_api.set_oracle_price("EUR", 4998978423)
# for tx in txs:
#     liquidator_api.add_tx(tx)
# print(liquidator_api.to_json())
