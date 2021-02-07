import time
import json
from violas_client import Wallet, Client
from bank import Bank, AccountView, TokenInfo

client = Client("violas_testnet")
print(client.bank_get_lock_amounts("b14bc3286e4b9b41c86022f2e614d721"))
# currency_code = "vBTC"
#
# def update_tokens_info(version):
#     bank = Bank()
#     state = client.get_account_state(client.BANK_OWNER_ADDRESS, version)
#     resource = state.get_token_info_store_resource(accrue_interest=False)
#     for index, token in enumerate(resource.tokens):
#         if index % 2 == 0:
#             token = json.loads(token.to_json())
#             currency_code = token.get("currency_code")
#             token["total_supply"] = resource.tokens[index+1].total_supply
#             token["contract_value"] = state.get_bank_amount(index)
#             state = client.get_account_state(client.ORACLE_OWNER_ADDRESS, version)
#             if state is not None:
#                 rate = state.oracle_get_exchange_rate(currency_code)
#             if rate:
#                 token["oracle_price"] = rate.value
#             bank.token_infos[currency_code] = TokenInfo.empty(**token)
#
#
# def assert_token_consistence(currency, token_infos):
#     local_info = Bank().get_token_info(currency)
#     assert token_infos[1].total_supply == local_info.total_supply
#     assert token_infos[0].total_reserves == local_info.total_reserves
#     assert token_infos[0].total_borrows == local_info.total_borrows
#     assert token_infos[0].borrow_index == local_info.borrow_index
#     print(token_infos[0].price, local_info.price)
#     assert token_infos[0].price == local_info.price
#     assert token_infos[0].collateral_factor == local_info.collateral_factor
#     assert token_infos[0].base_rate == local_info.base_rate
#     assert token_infos[0].rate_multiplier == local_info.rate_multiplier
#     assert token_infos[0].rate_jump_multiplier == local_info.rate_jump_multiplier
#     assert token_infos[0].rate_kink == local_info.rate_kink
#     assert token_infos[0].last_minute == local_info.last_minute
#
# version = 19254391
#
# update_tokens_info(version-1)
# bank = Bank()
# tx = client.get_transaction(version)
# bank.add_tx(tx)
# index = client.bank_get_currency_index(currency_code)
# token_info = client.get_account_state(client.BANK_OWNER_ADDRESS, version).get_token_info_store_resource(
#     accrue_interest=False).tokens[index:index + 2]
# assert_token_consistence(currency_code, token_info)
# version += 1

