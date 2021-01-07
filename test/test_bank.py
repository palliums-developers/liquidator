import time
from bank import Bank
from violas_client import Client, Wallet

def add_tx(account_address, seq):
    tx = client.get_account_transaction(account_address, seq)
    Bank().add_tx(tx)

def assert_account_consistence(address, tokens):
    if isinstance(address, bytes):
        address = address.hex()
    #借款数据
    borrows = Bank().accounts[address].borrow_amounts.amounts.get("USD")
    if borrows is None:
        assert tokens.borrows[0].principal == 0
    else:
        assert tokens.borrows[0].principal == Bank().accounts[address].borrow_amounts.amounts["USD"][0]
        assert tokens.borrows[0].interest_index == Bank().accounts[address].borrow_amounts.amounts["USD"][1]
    #存款数据
    print(tokens.ts[1].value, Bank().accounts[address].lock_amounts.amounts["USD"])
    assert tokens.ts[1].value == Bank().accounts[address].lock_amounts.amounts["USD"]

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

def publish_compound_module():
    wallet = Wallet.new()
    a1 = wallet.new_account()
    client.mint_coin(a1.address, 50_000_000, auth_key_prefix=a1.auth_key_prefix, currency_code="USD")
    client.bank_publish_module(a1)
    client.set_bank_module_address(a1.address)
    client.set_bank_owner_address(a1.address)
    seq = client.bank_publish(a1)
    add_tx(a1.address, seq)
    seq = client.bank_register_token(a1, "USD", a1.address, collater_factor=0.2, base_rate=0.15, rate_multiplier=0.2, rate_jump_mutiplier=0.4, rate_kink=0.8)
    add_tx(a1.address, seq)
    seq = client.bank_update_collateral_factor(a1, "USD", 0.5)
    add_tx(a1.address, seq)
    seq = client.bank_update_rate_model(a1, "USD", 0.2, 0.3, 0.4, 0.9)
    add_tx(a1.address, seq)
    price = client.get_account_state(client.ORACLE_OWNER_ADDRESS).oracle_get_exchange_rate("USD")
    Bank().set_oracle_price("USD", price.value)
    Bank().set_price("USD", price.value)
    return a1.address

client = Client("bj_testnet")
bank_module_address = publish_compound_module()
client.set_bank_module_address(bank_module_address)
client.set_bank_owner_address(bank_module_address)

def test_lock():
    wallet = Wallet.new()
    a1 = wallet.new_account()
    client.mint_coin(a1.address, 50_000_000, auth_key_prefix=a1.auth_key_prefix, currency_code="USD")
    seq = client.bank_publish(a1)
    add_tx(a1.address, seq)
    seq = client.bank_lock(a1, 10_000_000, currency_code="USD")
    add_tx(a1.address, seq)
    time.sleep(60)
    seq = client.bank_lock(a1, 500, currency_code="USD")
    add_tx(a1.address, seq)
    tokens = client.get_account_state(a1.address).get_tokens_resource()
    assert_account_consistence(a1.address, tokens)
    token_info = client.get_account_state(client.bank_module_address).get_token_info_store_resource().tokens[0:2]
    assert_token_consistence("USD", token_info)

def test_borrow():
    wallet = Wallet.new()
    a1 = wallet.new_account()
    client.mint_coin(a1.address, 50_000_000, auth_key_prefix=a1.auth_key_prefix, currency_code="USD")
    seq = client.bank_publish(a1)
    add_tx(a1.address, seq)
    seq = client.bank_lock(a1, 10_000_000, currency_code="USD")
    add_tx(a1.address, seq)
    time.sleep(60)
    seq = client.bank_borrow(a1, 500_000, currency_code="USD")
    add_tx(a1.address, seq)
    time.sleep(60)
    seq = client.bank_borrow(a1, 500_000, currency_code="USD")
    add_tx(a1.address, seq)
    time.sleep(60)
    seq = client.bank_lock(a1, 500_000, currency_code="USD")
    add_tx(a1.address, seq)
    tokens = client.get_account_state(a1.address).get_tokens_resource()
    assert_account_consistence(a1.address, tokens)
    token_info = client.get_account_state(client.bank_module_address).get_token_info_store_resource().tokens[0:2]
    assert_token_consistence("USD", token_info)

def test_redeem():
    wallet = Wallet.new()
    a1 = wallet.new_account()
    client.mint_coin(a1.address, 50_000_000, auth_key_prefix=a1.auth_key_prefix, currency_code="USD")
    seq = client.bank_publish(a1)
    add_tx(a1.address, seq)
    seq = client.bank_lock(a1, 10_000_000, currency_code="USD")
    add_tx(a1.address, seq)
    time.sleep(60)
    seq = client.bank_borrow(a1, 500_000, currency_code="USD")
    add_tx(a1.address, seq)
    seq = client.bank_borrow(a1, 500_000, currency_code="USD")
    add_tx(a1.address, seq)
    time.sleep(60)
    seq = client.bank_redeem(a1, 200_000, currency_code="USD")
    add_tx(a1.address, seq)

    token_info = client.get_account_state(client.bank_module_address).get_token_info_store_resource().tokens[0:2]
    assert_token_consistence("USD", token_info)
    tokens = client.get_account_state(a1.address).get_tokens_resource()
    assert_account_consistence(a1.address, tokens)

def test_repay_borrow():
    wallet = Wallet.new()
    a1 = wallet.new_account()
    client.mint_coin(a1.address, 50_000_000, auth_key_prefix=a1.auth_key_prefix, currency_code="USD")
    seq = client.bank_publish(a1)
    add_tx(a1.address, seq)
    seq = client.bank_lock(a1, 10_000_000, currency_code="USD")
    add_tx(a1.address, seq)
    seq = client.bank_borrow(a1, 500_000, currency_code="USD")
    add_tx(a1.address, seq)
    seq = client.bank_borrow(a1, 500_000, currency_code="USD")
    add_tx(a1.address, seq)
    time.sleep(60)
    seq = client.bank_repay_borrow(a1, 200_000, currency_code="USD")
    add_tx(a1.address, seq)

    token_info = client.get_account_state(client.bank_module_address).get_token_info_store_resource().tokens[0:2]
    assert_token_consistence("USD", token_info)
    tokens = client.get_account_state(a1.address).get_tokens_resource()
    assert_account_consistence(a1.address, tokens)

def test_liquidator_borrow():
    wallet = Wallet.new()
    a1 = wallet.new_account()
    a2 = wallet.new_account()
    client.mint_coin(a1.address, 50_000_000, auth_key_prefix=a1.auth_key_prefix, currency_code="USD")
    client.mint_coin(a2.address, 50_000_000, auth_key_prefix=a2.auth_key_prefix, currency_code="USD")
    seq = client.bank_publish(a1)
    add_tx(a1.address, seq)
    seq = client.bank_publish(a2)
    add_tx(a2.address, seq)
    seq = client.bank_enter(a2, 10_000_000, "USD")
    add_tx(a2.address, seq)
    seq = client.bank_lock(a1, 10_000_001, currency_code="USD")
    add_tx(a1.address, seq)
    seq = client.bank_lock(a2, 10_000_000, currency_code="USD")
    add_tx(a2.address, seq)
    seq = client.bank_borrow(a1, 5_000_000, currency_code="USD")
    add_tx(a1.address, seq)
    time.sleep(60)
    seq = client.bank_liquidate_borrow(a2, a1.address, "USD", "USD", 1)

    add_tx(a2.address, seq)

    token_info = client.get_account_state(client.bank_module_address).get_token_info_store_resource().tokens[0:2]
    assert_token_consistence("USD", token_info)
    tokens = client.get_account_state(a1.address).get_tokens_resource()
    assert_account_consistence(a1.address, tokens)
