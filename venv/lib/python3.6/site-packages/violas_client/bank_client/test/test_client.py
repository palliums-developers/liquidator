from violas_client import Client, Wallet
import time
module_address = "3e7f951e8f86a8b8c2aff288aa99753c"

client = Client()

def approximately_equal_to(a, b):
    a = int(a)
    b = int(b)
    return a in range(b-50, b+50)

def publish_bank_module():
    wallet = Wallet.new()
    module_account = wallet.new_account()
    client.mint_coin(module_account.address, 2_000_000_000, auth_key_prefix=module_account.auth_key_prefix)
    client.bank_publish_contract(module_account)
    client.set_bank_module_address(module_account.address)
    client.bank_publish(module_account)
    client.bank_register_token(module_account, module_account.address, 0.5, currency_code="LBR")
    client.bank_register_token(module_account, module_account.address, 0.5, currency_code="Coin1")
    client.bank_register_token(module_account, module_account.address, 0.5, currency_code="Coin2")

    client.bank_update_price(module_account, 0.1, currency_code="LBR")
    client.bank_update_price(module_account, 0.1, currency_code="LBR")
    client.bank_update_price(module_account, 0.1, currency_code="LBR")
    return module_account.address_hex

def test_init():
    address = publish_bank_module()
    print(address)

def test_lock():
    wallet = Wallet.new()
    a1 = wallet.new_account()
    module_address = publish_bank_module()
    client.set_bank_module_address(module_address)
    client.mint_coin(a1.address, 3_000_000_000, auth_key_prefix=a1.auth_key_prefix)
    client.bank_publish(a1)
    client.bank_enter(a1, 2_000_000_000, currency_code="LBR")
    client.bank_lock(a1, 1_000_000_000, currency_code="LBR")
    assert 1_000_000_000 == client.bank_get_amount(a1.address, currency_code="LBR")
    assert approximately_equal_to(client.bank_get_lock_amount(a1.address, currency_code="LBR"), 1_000_000_000)
    assert 0 == client.bank_get_lock_rate("LBR")

def test_redeem():
    wallet = Wallet.new()
    a1 = wallet.new_account()
    module_address = publish_bank_module()
    client.set_bank_module_address(module_address)
    client.mint_coin(a1.address, 3_000_000_000, auth_key_prefix=a1.auth_key_prefix)
    client.bank_publish(a1)
    client.bank_enter(a1, 2_000_000_000, currency_code="LBR")
    client.bank_lock(a1, 1_000_000_000, currency_code="LBR")
    time.sleep(60)
    client.bank_redeem(a1, currency_code="LBR")
    assert approximately_equal_to(client.bank_get_amount(a1.address, currency_code="LBR"), 2_000_000_000)

def test_borrow():
    wallet = Wallet.new()
    a1 = wallet.new_account()
    module_address = publish_bank_module()
    client.set_bank_module_address(module_address)
    client.mint_coin(a1.address, 3_000_000_000, auth_key_prefix=a1.auth_key_prefix)
    client.bank_publish(a1)
    client.bank_enter(a1, 2_000_000_000, currency_code="LBR")
    client.bank_lock(a1, 1_000_000_000, currency_code="LBR")
    client.bank_borrow(a1, 100_000_000, currency_code="LBR")
    assert approximately_equal_to(client.bank_get_borrow_amount(a1.address, currency_code="LBR")[1], 100_000_000)
    assert approximately_equal_to(client.bank_get_amount(a1.address, currency_code="LBR"), 1_000_000_000+100_000_000)

def test_repay_borrow():
    wallet = Wallet.new()
    a1 = wallet.new_account()
    module_address = publish_bank_module()
    client.set_bank_module_address(module_address)
    client.mint_coin(a1.address, 3_000_000_000, auth_key_prefix=a1.auth_key_prefix)
    client.bank_publish(a1)
    client.bank_enter(a1, 2_000_000_000, currency_code="LBR")
    client.bank_lock(a1, 1_000_000_000, currency_code="LBR")
    client.bank_borrow(a1, 100_000_000, currency_code="LBR")
    client.bank_repay_borrow(a1, currency_code="LBR")
    assert approximately_equal_to(client.bank_get_borrow_amount(a1.address, currency_code="LBR")[0], 0)
    assert approximately_equal_to(client.bank_get_amount(a1.address, currency_code="LBR"), 1_000_000_000)

def test_bank_get_supply_rate():
    wallet = Wallet.new()
    a1 = wallet.new_account()
    a2 = wallet.new_account()
    module_address = publish_bank_module()
    client.set_bank_module_address(module_address)
    client.mint_coin(a1.address, 3_000_000_000, auth_key_prefix=a1.auth_key_prefix)
    client.mint_coin(a2.address, 3_000_000_000, auth_key_prefix=a2.auth_key_prefix)
    client.bank_publish(a1)
    client.bank_publish(a2)
    client.bank_enter(a1, 2_000_000_000, currency_code="LBR")
    client.bank_enter(a2, 2_000_000_000, currency_code="LBR")

    client.bank_lock(a1, 1_000_000_000, currency_code="LBR")
    client.bank_borrow(a1, 100_000_000, currency_code="LBR")
    client.bank_lock(a2, 1_000_000_000, currency_code="LBR")
    lock_rate = client.bank_get_lock_rate("LBR")
    time.sleep(60)
    lock_amount = client.bank_get_lock_amount(a2.address, currency_code="LBR")
    assert approximately_equal_to(lock_amount, 1_000_000_000+1_000_000_000*lock_rate)
    client.bank_redeem(a2, currency_code="LBR")
    assert approximately_equal_to(2_000_000_000+lock_amount-1_000_000_000, client.bank_get_amount(a2.address, currency_code="LBR"))

def test_bank_get_borrow_rate():
    wallet = Wallet.new()
    a1 = wallet.new_account()
    module_address = publish_bank_module()
    client.set_bank_module_address(module_address)
    client.mint_coin(a1.address, 3_000_000_000, auth_key_prefix=a1.auth_key_prefix)
    client.bank_publish(a1)
    client.bank_enter(a1, 2_000_000_000, currency_code="LBR")
    client.bank_lock(a1, 1_000_000_000, currency_code="LBR")
    client.bank_borrow(a1, 100_000_000, currency_code="LBR")
    borrow_rate = client.bank_get_borrow_rate(currency_code="LBR")
    time.sleep(120)
    _, borrow_amount = client.bank_get_borrow_amount(a1.address, currency_code="LBR")
    assert approximately_equal_to(borrow_amount, 100_000_000+100_000_000*borrow_rate*2)
    client.bank_repay_borrow(a1, currency_code="LBR")
    assert approximately_equal_to(client.bank_get_amount(a1.address, currency_code="LBR"), 1_000_000_000-100_000_000*borrow_rate*2)

