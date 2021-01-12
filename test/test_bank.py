import time
import json
from violas_client import Wallet, Client
from bank import Bank, AccountView, TokenInfo

client = Client("bj_testnet")
currency_code = "USD"

def update_tokens_info():
    bank = Bank()
    state = client.get_account_state(client.BANK_OWNER_ADDRESS)
    resource = state.get_token_info_store_resource()
    for index, token in enumerate(resource.tokens):
        if index % 2 == 0:
            token = json.loads(token.to_json())
            currency_code = token.get("currency_code")
            token["total_supply"] = resource.tokens[index+1].total_supply
            token["contract_value"] = state.get_bank_amount(index)
            rate = client.oracle_get_exchange_rate(currency_code)
            if rate:
                token["oracle_price"] = rate.value
            bank.token_infos[currency_code] = TokenInfo.empty(**token)

update_tokens_info()

def update_account_info(addr):
    bank = Bank()
    state = client.get_account_state(addr)
    resource = state.get_tokens_resource()
    account_view = AccountView(addr)

    for i, token in enumerate(resource.ts):
        if i % 2 == 1:
            currency_code = client.bank_get_currency_code(token.index)
            account_view.lock_amounts.add_original_amount(currency_code, token.value)
    for i, borrow in enumerate(resource.borrows):
        if i % 2 == 0:
            currency_code = client.bank_get_currency_code(i)
            account_view.borrow_amounts.add_amount(currency_code, borrow.principal, borrow.interest_index)
    bank.accounts[addr] = account_view

def add_tx(account_address, seq):
    tx = client.get_account_transaction(account_address, seq)
    Bank().add_tx(tx)

def assert_account_consistence(address, tokens, currency_code, index):
    if isinstance(address, bytes):
        address = address.hex()
    #借款数据
    borrows = Bank().accounts[address].borrow_amounts.amounts.get(currency_code)
    if borrows is None:
        assert tokens.borrows[index].principal == 0
    else:
        assert tokens.borrows[index].principal == Bank().accounts[address].borrow_amounts.amounts[currency_code][0]
        assert tokens.borrows[index].interest_index == Bank().accounts[address].borrow_amounts.amounts[currency_code][1]
    #存款数据
    index = client.bank_get_currency_index(currency_code)+1
    assert tokens.ts[index].value == Bank().accounts[address].lock_amounts.amounts[currency_code]

def assert_token_consistence(currency, token_infos):
    local_info = Bank().get_token_info(currency)
    assert token_infos[1].total_supply == local_info.total_supply
    assert token_infos[0].total_reserves == local_info.total_reserves
    assert token_infos[0].total_borrows == local_info.total_borrows
    assert token_infos[0].borrow_index == local_info.borrow_index
    assert token_infos[0].price == local_info.price
    assert token_infos[0].collateral_factor == local_info.collateral_factor
    assert token_infos[0].base_rate == local_info.base_rate
    assert token_infos[0].rate_multiplier == local_info.rate_multiplier
    assert token_infos[0].rate_jump_multiplier == local_info.rate_jump_multiplier
    assert token_infos[0].rate_kink == local_info.rate_kink
    assert token_infos[0].last_minute == local_info.last_minute

def test_lock():
    wallet = Wallet.new()
    a1 = wallet.new_account()
    client.mint_coin(a1.address, 50_000_000, auth_key_prefix=a1.auth_key_prefix, currency_code=currency_code)
    seq = client.bank_publish(a1)
    add_tx(a1.address, seq)
    seq = client.bank_lock(a1, 10_000_000, currency_code=currency_code)
    add_tx(a1.address, seq)
    time.sleep(60)
    seq = client.bank_lock(a1, 500, currency_code=currency_code)
    add_tx(a1.address, seq)
    tokens = client.get_account_state(a1.address).get_tokens_resource()
    index = client.bank_get_currency_index(currency_code)
    assert_account_consistence(a1.address, tokens, currency_code, index)
    token_info = client.get_account_state(client.BANK_OWNER_ADDRESS).get_token_info_store_resource().tokens[index: index+2]
    assert_token_consistence(currency_code, token_info)

def test_borrow():
    wallet = Wallet.new()
    a1 = wallet.new_account()
    client.mint_coin(a1.address, 50_000_000, auth_key_prefix=a1.auth_key_prefix, currency_code=currency_code)
    seq = client.bank_publish(a1)
    add_tx(a1.address, seq)
    seq = client.bank_lock(a1, 10_000_000, currency_code=currency_code)
    add_tx(a1.address, seq)
    time.sleep(60)
    seq = client.bank_borrow(a1, 500_000, currency_code=currency_code)
    add_tx(a1.address, seq)
    time.sleep(60)
    seq = client.bank_borrow(a1, 500_000, currency_code=currency_code)
    add_tx(a1.address, seq)
    time.sleep(60)
    seq = client.bank_lock(a1, 500_000, currency_code=currency_code)
    add_tx(a1.address, seq)
    tokens = client.get_account_state(a1.address).get_tokens_resource()
    index = client.bank_get_currency_index(currency_code)
    assert_account_consistence(a1.address, tokens, currency_code, index)
    token_info = client.get_account_state(client.BANK_OWNER_ADDRESS).get_token_info_store_resource().tokens[index:index+2]
    assert_token_consistence(currency_code, token_info)

def test_redeem():
    wallet = Wallet.new()
    a1 = wallet.new_account()
    client.mint_coin(a1.address, 50_000_000, auth_key_prefix=a1.auth_key_prefix, currency_code=currency_code)
    seq = client.bank_publish(a1)
    add_tx(a1.address, seq)
    seq = client.bank_lock(a1, 10_000_000, currency_code=currency_code)
    add_tx(a1.address, seq)
    time.sleep(60)
    seq = client.bank_borrow(a1, 500_000, currency_code=currency_code)
    add_tx(a1.address, seq)
    seq = client.bank_borrow(a1, 500_000, currency_code=currency_code)
    add_tx(a1.address, seq)
    time.sleep(60)
    seq = client.bank_redeem(a1, 200_000, currency_code=currency_code)
    add_tx(a1.address, seq)

    index = client.bank_get_currency_index(currency_code)
    token_info = client.get_account_state(client.BANK_OWNER_ADDRESS).get_token_info_store_resource().tokens[index:index+2]
    assert_token_consistence(currency_code, token_info)
    tokens = client.get_account_state(a1.address).get_tokens_resource()
    index = client.bank_get_currency_index(currency_code)
    assert_account_consistence(a1.address, tokens, currency_code, index)

def test_repay_borrow():
    wallet = Wallet.new()
    a1 = wallet.new_account()
    client.mint_coin(a1.address, 50_000_000, auth_key_prefix=a1.auth_key_prefix, currency_code=currency_code)
    seq = client.bank_publish(a1)
    add_tx(a1.address, seq)
    seq = client.bank_lock(a1, 10_000_000, currency_code=currency_code)
    add_tx(a1.address, seq)
    seq = client.bank_borrow(a1, 500_000, currency_code=currency_code)
    add_tx(a1.address, seq)
    seq = client.bank_borrow(a1, 500_000, currency_code=currency_code)
    add_tx(a1.address, seq)
    time.sleep(60)
    seq = client.bank_repay_borrow(a1, 200_000, currency_code=currency_code)
    add_tx(a1.address, seq)

    index = client.bank_get_currency_index(currency_code)
    token_info = client.get_account_state(client.BANK_OWNER_ADDRESS).get_token_info_store_resource().tokens[index:index+2]
    assert_token_consistence(currency_code, token_info)
    tokens = client.get_account_state(a1.address).get_tokens_resource()
    assert_account_consistence(a1.address, tokens, currency_code, index)

def test_liquidator_borrow():
    wallet = Wallet.new()
    a1 = wallet.new_account()
    a2 = wallet.new_account()
    client.mint_coin(a1.address, 5_000_000_000, auth_key_prefix=a1.auth_key_prefix, currency_code=currency_code)
    client.mint_coin(a2.address, 5_000_000_000, auth_key_prefix=a2.auth_key_prefix, currency_code=currency_code)
    seq = client.bank_publish(a1)
    add_tx(a1.address, seq)
    seq = client.bank_publish(a2)
    add_tx(a2.address, seq)
    seq = client.bank_enter(a2, 1_000_000_000, currency_code)
    add_tx(a2.address, seq)
    seq = client.bank_lock(a1, 1_000_000_001, currency_code=currency_code)
    add_tx(a1.address, seq)
    seq = client.bank_lock(a2, 1_000_000_000, currency_code=currency_code)
    add_tx(a2.address, seq)
    seq = client.bank_borrow(a1, 500_000_000-1, currency_code=currency_code)
    add_tx(a1.address, seq)
    time.sleep(60)
    seq = client.bank_liquidate_borrow(a2, a1.address, currency_code, currency_code, 1)

    add_tx(a2.address, seq)

    index = client.bank_get_currency_index(currency_code)
    token_info = client.get_account_state(client.BANK_OWNER_ADDRESS).get_token_info_store_resource().tokens[index:index+2]
    assert_token_consistence(currency_code, token_info)
    tokens = client.get_account_state(a1.address).get_tokens_resource()
    assert_account_consistence(a1.address, tokens, currency_code, index)
    tokens = client.get_account_state(a2.address).get_tokens_resource()
    assert_account_consistence(a2.address, tokens, currency_code, index)