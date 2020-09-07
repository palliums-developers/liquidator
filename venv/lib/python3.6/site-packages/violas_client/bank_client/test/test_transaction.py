from violas_client import Client, Wallet
from banktypes.bytecode import CodeType
from lbrtypes.bytecode import CodeType as LibraCodeType

def test_get_code_type():
    wallet = Wallet.new()
    module_account = wallet.new_account()
    client = Client()
    client.mint_coin(module_account.address, 2_000_000_000, auth_key_prefix=module_account.auth_key_prefix)
    seq = client.bank_publish_contract(module_account)
    assert client.get_account_transaction(module_account.address, seq).get_code_type() == LibraCodeType.MODULE
    client.set_bank_module_address(module_account.address)
    seq = client.bank_publish(module_account)
    assert client.get_account_transaction(module_account.address, seq).get_code_type() == CodeType.PUBLISH

    seq = client.bank_register_token(module_account, module_account.address, 0.5, currency_code="LBR")
    assert client.get_account_transaction(module_account.address, seq).get_code_type() == CodeType.REGISTER_TOKEN
    seq = client.bank_update_price(module_account, 0.1, currency_code="LBR")
    assert client.get_account_transaction(module_account.address, seq).get_code_type() == CodeType.UPDATE_PRICE

    a1 = wallet.new_account()
    client.mint_coin(a1.address, 3_000_000_000, auth_key_prefix=a1.auth_key_prefix)
    seq = client.bank_publish(a1)
    assert client.get_account_transaction(a1.address, seq).get_code_type() == CodeType.PUBLISH

    seq = client.bank_enter(a1, 2_000_000_000, currency_code="LBR")
    assert client.get_account_transaction(a1.address, seq).get_code_type() == CodeType.ENTER_BANK

    seq = client.bank_lock(a1, 1_000_000_000, currency_code="LBR")
    assert client.get_account_transaction(a1.address, seq).get_code_type() == CodeType.LOCK

    seq = client.bank_borrow(a1, 1_000, currency_code="LBR")
    assert client.get_account_transaction(a1.address, seq).get_code_type() == CodeType.BORROW

    seq = client.bank_repay_borrow(a1, currency_code="LBR")
    assert client.get_account_transaction(a1.address, seq).get_code_type() == CodeType.REPAY_BORROW

    seq = client.bank_redeem(a1, currency_code="LBR")
    assert client.get_account_transaction(a1.address, seq).get_code_type() == CodeType.REDEEM

    seq = client.bank_exit(a1, 1_000_000_000, currency_code="LBR")
    assert client.get_account_transaction(a1.address, seq).get_code_type() == CodeType.EXIT_BANK


def test_get_amount():
    wallet = Wallet.new()
    module_account = wallet.new_account()
    client = Client()
    client.mint_coin(module_account.address, 2_000_000_000, auth_key_prefix=module_account.auth_key_prefix)
    seq = client.bank_publish_contract(module_account)
    assert client.get_account_transaction(module_account.address, seq).get_amount() == None
    client.set_bank_module_address(module_account.address)
    seq = client.bank_publish(module_account)
    assert client.get_account_transaction(module_account.address, seq).get_amount() == None

    seq = client.bank_register_token(module_account, module_account.address, 0.5, currency_code="LBR")
    assert client.get_account_transaction(module_account.address, seq).get_amount() == None
    seq = client.bank_update_price(module_account, 0.1, currency_code="LBR")
    assert client.get_account_transaction(module_account.address, seq).get_amount() == None

    a1 = wallet.new_account()
    client.mint_coin(a1.address, 3_000_000_000, auth_key_prefix=a1.auth_key_prefix)
    seq = client.bank_publish(a1)
    assert client.get_account_transaction(a1.address, seq).get_amount() == None
    seq = client.bank_enter(a1, 2_000_000_000, currency_code="LBR")
    assert client.get_account_transaction(a1.address, seq).get_amount() == 2_000_000_000

    seq = client.bank_lock(a1, 1_000_000_000, currency_code="LBR")
    assert client.get_account_transaction(a1.address, seq).get_amount() == 1_000_000_000

    seq = client.bank_borrow(a1, 1_000, currency_code="LBR")
    assert client.get_account_transaction(a1.address, seq).get_amount() == 1_000

    seq = client.bank_repay_borrow(a1, amount=100, currency_code="LBR")
    assert client.get_account_transaction(a1.address, seq).get_amount() == 100

    seq = client.bank_redeem(a1, currency_code="LBR", amount=100)
    assert client.get_account_transaction(a1.address, seq).get_amount() == 100

    seq = client.bank_exit(a1, 1_000_000_000, currency_code="LBR")
    assert client.get_account_transaction(a1.address, seq).get_amount() == 1_000_000_000


def test_get_currency_code():
    wallet = Wallet.new()
    module_account = wallet.new_account()
    client = Client()
    client.mint_coin(module_account.address, 2_000_000_000, auth_key_prefix=module_account.auth_key_prefix)
    seq = client.bank_publish_contract(module_account)
    assert client.get_account_transaction(module_account.address, seq).get_currency_code() == None
    client.set_bank_module_address(module_account.address)
    seq = client.bank_publish(module_account)
    assert client.get_account_transaction(module_account.address, seq).get_currency_code() == None

    seq = client.bank_register_token(module_account, module_account.address, 0.5, currency_code="LBR")
    assert client.get_account_transaction(module_account.address, seq).get_currency_code() == "LBR"
    seq = client.bank_update_price(module_account, 0.1, currency_code="LBR")
    assert client.get_account_transaction(module_account.address, seq).get_currency_code() == "LBR"

    a1 = wallet.new_account()
    client.mint_coin(a1.address, 3_000_000_000, auth_key_prefix=a1.auth_key_prefix)
    seq = client.bank_publish(a1)
    assert client.get_account_transaction(a1.address, seq).get_currency_code() == None
    seq = client.bank_enter(a1, 2_000_000_000, currency_code="LBR")
    assert client.get_account_transaction(a1.address, seq).get_currency_code() == "LBR"

    seq = client.bank_lock(a1, 1_000_000_000, currency_code="LBR")
    assert client.get_account_transaction(a1.address, seq).get_currency_code() == "LBR"

    seq = client.bank_borrow(a1, 1_000, currency_code="LBR")
    assert client.get_account_transaction(a1.address, seq).get_currency_code() == "LBR"

    seq = client.bank_repay_borrow(a1, amount=100, currency_code="LBR")
    assert client.get_account_transaction(a1.address, seq).get_currency_code() == "LBR"

    seq = client.bank_redeem(a1, amount=100, currency_code="LBR")
    assert client.get_account_transaction(a1.address, seq).get_currency_code() == "LBR"

    seq = client.bank_exit(a1, 1_000_000_000, currency_code="LBR")
    assert client.get_account_transaction(a1.address, seq).get_currency_code() == "LBR"

def test_get_data():
    data = "data"
    data_hex = b"data".hex()
    wallet = Wallet.new()
    module_account = wallet.new_account()
    client = Client()
    client.mint_coin(module_account.address, 2_000_000_000, auth_key_prefix=module_account.auth_key_prefix)
    seq = client.bank_publish_contract(module_account)
    assert client.get_account_transaction(module_account.address, seq).get_data() == None
    client.set_bank_module_address(module_account.address)
    seq = client.bank_publish(module_account, data=data)
    assert client.get_account_transaction(module_account.address, seq).get_data() == data_hex

    seq = client.bank_register_token(module_account, module_account.address, 0.5, currency_code="LBR", data=data)
    assert client.get_account_transaction(module_account.address, seq).get_data() == data_hex
    seq = client.bank_update_price(module_account, 0.1, currency_code="LBR")
    assert client.get_account_transaction(module_account.address, seq).get_data() == None

    a1 = wallet.new_account()
    client.mint_coin(a1.address, 3_000_000_000, auth_key_prefix=a1.auth_key_prefix)
    seq = client.bank_publish(a1, data=data)
    assert client.get_account_transaction(a1.address, seq).get_data() == data_hex
    seq = client.bank_enter(a1, 2_000_000_000, currency_code="LBR")
    assert client.get_account_transaction(a1.address, seq).get_data() == None

    seq = client.bank_lock(a1, 1_000_000_000, currency_code="LBR", data=data)
    assert client.get_account_transaction(a1.address, seq).get_data() == data_hex

    seq = client.bank_borrow(a1, 1_000, currency_code="LBR", data=data)
    assert client.get_account_transaction(a1.address, seq).get_data() == data_hex

    seq = client.bank_repay_borrow(a1, amount=100, currency_code="LBR", data=data)
    assert client.get_account_transaction(a1.address, seq).get_data() == data_hex

    seq = client.bank_redeem(a1, amount=100, currency_code="LBR", data=data)
    assert client.get_account_transaction(a1.address, seq).get_data() == data_hex

    seq = client.bank_exit(a1, 1_000_000_000, currency_code="LBR")
    assert client.get_account_transaction(a1.address, seq).get_data() == None
