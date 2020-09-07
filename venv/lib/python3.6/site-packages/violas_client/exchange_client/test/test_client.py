from violas_client import Wallet, Client

client = Client()

def test_initilaize():
    wallet = Wallet.new()
    module_account = wallet.new_account()
    client.mint_coin(module_account.address, 10_000_000, auth_key_prefix=module_account.auth_key_prefix, is_blocking=True)
    client.swap_publish_contract(module_account)
    client.set_exchange_module_address(module_account.address)
    client.swap_initialize(module_account)
    resource = client.get_account_state(module_account.address).swap_get_reserves_resource()
    assert resource is not None

def test_publish_reserve():
    wallet = Wallet.new()
    module_account = wallet.new_account()
    client.mint_coin(module_account.address, 10_000_000, auth_key_prefix=module_account.auth_key_prefix, is_blocking=True)
    client.swap_publish_contract(module_account)
    client.set_exchange_module_address(module_account.address)
    client.swap_initialize(module_account)
    client.swap_add_currency(module_account, "Coin1")
    resource = client.get_account_state(module_account.address).swap_get_balance("Coin1")
    assert resource is not None

def test_add_liquidity():
    wallet = Wallet.new()
    
    module_account = wallet.new_account()
    client.mint_coin(module_account.address, 10_000_000, auth_key_prefix=module_account.auth_key_prefix, is_blocking=True)
    client.swap_publish_contract(module_account)
    client.set_exchange_module_address(module_account.address)
    client.swap_initialize(module_account)
    client.swap_add_currency(module_account, "LBR")
    client.swap_add_currency(module_account, "Coin1")

    liquidity_account = wallet.new_account()
    client.mint_coin(liquidity_account.address, 10_000_000, auth_key_prefix=liquidity_account.auth_key_prefix, is_blocking=True)
    client.add_currency_to_account(liquidity_account, "Coin1")
    client.mint_coin(liquidity_account.address, 10_000_000, currency_code="Coin1", auth_key_prefix=liquidity_account.auth_key_prefix, is_blocking=True)

    swap_account = wallet.new_account()
    client.mint_coin(swap_account.address, 10_000_000, auth_key_prefix=swap_account.auth_key_prefix, is_blocking=True)
    client.add_currency_to_account(swap_account, "Coin1")
    client.mint_coin(swap_account.address, 10_000_000, currency_code="Coin1", auth_key_prefix=swap_account.auth_key_prefix, is_blocking=True)

    lbr_before_balance = client.get_balance(liquidity_account.address, "LBR")
    coin1_before_balance = client.get_balance(liquidity_account.address, "Coin1")
    client.swap_add_liquidity(liquidity_account, "LBR", "Coin1", 1_000_000, 321_432)
    lbr_after_balance = client.get_balance(liquidity_account.address, "LBR")
    coin1_after_balance = client.get_balance(liquidity_account.address, "Coin1")
    assert lbr_before_balance - lbr_after_balance == 1_000_000
    assert coin1_before_balance - coin1_after_balance == 321_432
    liquidity_balance = client.swap_get_liquidity_balances(liquidity_account.address)
    assert liquidity_balance[0]["liquidity"] == int((1_000_000*321_432)**0.5)

def test_remove_liquidity():
    wallet = Wallet.new()
    
    module_account = wallet.new_account()
    client.mint_coin(module_account.address, 10_000_000, auth_key_prefix=module_account.auth_key_prefix, is_blocking=True)
    client.swap_publish_contract(module_account)
    client.set_exchange_module_address(module_account.address)
    client.swap_initialize(module_account)
    client.swap_add_currency(module_account, "LBR")
    client.swap_add_currency(module_account, "Coin1")

    liquidity_account = wallet.new_account()
    client.mint_coin(liquidity_account.address, 10_000_000, auth_key_prefix=liquidity_account.auth_key_prefix, is_blocking=True)
    client.add_currency_to_account(liquidity_account, "Coin1")
    client.mint_coin(liquidity_account.address, 10_000_000, currency_code="Coin1", auth_key_prefix=liquidity_account.auth_key_prefix, is_blocking=True)

    swap_account = wallet.new_account()
    client.mint_coin(swap_account.address, 10_000_000, auth_key_prefix=swap_account.auth_key_prefix, is_blocking=True)
    client.add_currency_to_account(swap_account, "Coin1")
    client.mint_coin(swap_account.address, 10_000_000, currency_code="Coin1", auth_key_prefix=swap_account.auth_key_prefix, is_blocking=True)

    client.swap_add_liquidity(liquidity_account, "LBR", "Coin1", 1_000_000, 321_432)
    client.swap_remove_liquidity(liquidity_account, "Coin1", "LBR", int((1_000_000 * 321_432) ** 0.5), amounta_min=321_432, amountb_min=1_000_000)

def test_swap():
    wallet = Wallet.new()
    
    module_account = wallet.new_account()
    client.mint_coin(module_account.address, 10_000_000, auth_key_prefix=module_account.auth_key_prefix, is_blocking=True)
    client.swap_publish_contract(module_account)
    client.set_exchange_module_address(module_account.address)
    client.swap_initialize(module_account)
    client.swap_add_currency(module_account, "LBR")
    client.swap_add_currency(module_account, "Coin1")
    client.swap_add_currency(module_account, "Coin2")

    liquidity_account = wallet.new_account()
    client.mint_coin(liquidity_account.address, 10_000_000, auth_key_prefix=liquidity_account.auth_key_prefix, is_blocking=True)
    client.add_currency_to_account(liquidity_account, "Coin1")
    client.mint_coin(liquidity_account.address, 10_000_000, currency_code="Coin1", auth_key_prefix=liquidity_account.auth_key_prefix, is_blocking=True)
    client.add_currency_to_account(liquidity_account, "Coin2")
    client.mint_coin(liquidity_account.address, 10_000_000, currency_code="Coin2", auth_key_prefix=liquidity_account.auth_key_prefix, is_blocking=True)

    swap_account = wallet.new_account()
    client.mint_coin(swap_account.address, 10_000_000, auth_key_prefix=swap_account.auth_key_prefix, is_blocking=True)
    client.add_currency_to_account(swap_account, "Coin1")
    client.mint_coin(swap_account.address, 10_000_000, currency_code="Coin1", auth_key_prefix=swap_account.auth_key_prefix, is_blocking=True)
    client.add_currency_to_account(swap_account, "Coin2")
    client.mint_coin(swap_account.address, 10_000_000, currency_code="Coin2", auth_key_prefix=swap_account.auth_key_prefix, is_blocking=True)

    client.swap_add_liquidity(liquidity_account, "LBR", "Coin1", 123_321, 321_432)
    client.swap_add_liquidity(liquidity_account, "Coin2", "Coin1", 321_432, 321_432)

    (expected_amount, out) = client.swap_get_swap_output_amount("Coin1", "LBR", 1000)
    before_amount = client.get_balance(swap_account.address, "LBR")
    client.swap(swap_account, "Coin1", "LBR", 1000, expected_amount)
    after_amount = client.get_balance(swap_account.address, "LBR")
    assert after_amount - before_amount == expected_amount

    (expected_amount, out) = client.swap_get_swap_output_amount("Coin1", "LBR", 1000)
    before_amount = client.get_balance(liquidity_account.address, "LBR")
    client.swap(swap_account, "Coin1", "LBR", 1000, expected_amount, receiver_address=liquidity_account.address)
    after_amount = client.get_balance(liquidity_account.address, "LBR")
    assert after_amount - before_amount == expected_amount

def test_swap_get_liquidity_balances():
    wallet = Wallet.new()
    
    module_account = wallet.new_account()
    client.mint_coin(module_account.address, 10_000_000, auth_key_prefix=module_account.auth_key_prefix, is_blocking=True)
    client.swap_publish_contract(module_account)
    client.set_exchange_module_address(module_account.address)
    client.swap_initialize(module_account)
    client.swap_add_currency(module_account, "LBR")
    client.swap_add_currency(module_account, "Coin1")
    client.swap_add_currency(module_account, "Coin2")

    liquidity_account = wallet.new_account()
    client.mint_coin(liquidity_account.address, 10_000_000, auth_key_prefix=liquidity_account.auth_key_prefix, is_blocking=True)
    client.add_currency_to_account(liquidity_account, "Coin1")
    client.mint_coin(liquidity_account.address, 10_000_000, currency_code="Coin1", auth_key_prefix=liquidity_account.auth_key_prefix, is_blocking=True)
    client.add_currency_to_account(liquidity_account, "Coin2")
    client.mint_coin(liquidity_account.address, 10_000_000, currency_code="Coin2", auth_key_prefix=liquidity_account.auth_key_prefix,is_blocking=True)

    swap_account = wallet.new_account()
    client.mint_coin(swap_account.address, 10_000_000, auth_key_prefix=swap_account.auth_key_prefix, is_blocking=True)
    client.add_currency_to_account(swap_account, "Coin1")
    client.mint_coin(swap_account.address, 10_000_000, currency_code="Coin1", auth_key_prefix=swap_account.auth_key_prefix,is_blocking=True)
    client.add_currency_to_account(swap_account, "Coin2")
    client.mint_coin(swap_account.address, 10_000_000, currency_code="Coin2", auth_key_prefix=swap_account.auth_key_prefix, is_blocking=True)

    client.swap_add_liquidity(liquidity_account, "LBR", "Coin1", 2344532, 342566)
    client.swap_add_liquidity(liquidity_account, "LBR", "Coin1", 5324232, 323435)
    client.swap(swap_account, "Coin1", "LBR", 1000)
    blb = client.get_balance(liquidity_account.address, "LBR")
    bc1b = client.get_balance(liquidity_account.address, "Coin1")
    all = client.swap_get_liquidity_balances(liquidity_account.address)[0]
    client.swap_remove_liquidity(liquidity_account, "Coin1", "LBR", all["liquidity"])
    alb = client.get_balance(liquidity_account.address, "LBR")
    ac1b = client.get_balance(liquidity_account.address, "Coin1")
    assert alb - blb == all["LBR"]
    assert ac1b - bc1b == all["Coin1"]

def test_swap_get_swap_output_amount():
    wallet = Wallet.new()
    
    module_account = wallet.new_account()
    client.mint_coin(module_account.address, 10_000_000, auth_key_prefix=module_account.auth_key_prefix, is_blocking=True)
    client.swap_publish_contract(module_account)
    client.set_exchange_module_address(module_account.address)
    client.swap_initialize(module_account)
    client.swap_add_currency(module_account, "LBR")
    client.swap_add_currency(module_account, "Coin1")
    client.swap_add_currency(module_account, "Coin2")

    liquidity_account = wallet.new_account()
    client.mint_coin(liquidity_account.address, 10_000_000, auth_key_prefix=liquidity_account.auth_key_prefix, is_blocking=True)
    client.add_currency_to_account(liquidity_account, "Coin1")
    client.mint_coin(liquidity_account.address, 10_000_000, currency_code="Coin1",auth_key_prefix=liquidity_account.auth_key_prefix,is_blocking=True)
    client.add_currency_to_account(liquidity_account, "Coin2")
    client.mint_coin(liquidity_account.address, 10_000_000, currency_code="Coin2",auth_key_prefix=liquidity_account.auth_key_prefix,is_blocking=True)

    swap_account = wallet.new_account()
    client.mint_coin(swap_account.address, 10_000_000, auth_key_prefix=swap_account.auth_key_prefix,is_blocking=True)
    client.add_currency_to_account(swap_account, "Coin1")
    client.mint_coin(swap_account.address, 10_000_000, currency_code="Coin1",auth_key_prefix=swap_account.auth_key_prefix,is_blocking=True)
    client.add_currency_to_account(swap_account, "Coin2")
    client.mint_coin(swap_account.address, 10_000_000, currency_code="Coin2",auth_key_prefix=swap_account.auth_key_prefix,is_blocking=True)

    client.swap_add_liquidity(liquidity_account, "LBR", "Coin1", 342423, 435435)
    client.swap_add_liquidity(liquidity_account, "Coin2", "Coin1", 453452, 243244)
    out, _ = client.swap_get_swap_output_amount("Coin2", "LBR", 100_000)
    bb = client.get_balance(swap_account.address, "LBR")
    client.swap(swap_account, "Coin2", "LBR", 100_000)
    ab = client.get_balance(swap_account.address, "LBR")
    assert ab - bb == out

def test_swap_get_swap_input_amount():
    wallet = Wallet.new()
    
    module_account = wallet.new_account()
    client.mint_coin(module_account.address, 10_000_000, auth_key_prefix=module_account.auth_key_prefix, is_blocking=True)
    client.swap_publish_contract(module_account)
    client.set_exchange_module_address(module_account.address)
    client.swap_initialize(module_account)
    client.swap_add_currency(module_account, "LBR")
    client.swap_add_currency(module_account, "Coin1")
    client.swap_add_currency(module_account, "Coin2")

    liquidity_account = wallet.new_account()
    client.mint_coin(liquidity_account.address, 10_000_000, auth_key_prefix=liquidity_account.auth_key_prefix, is_blocking=True)
    client.add_currency_to_account(liquidity_account, "Coin1")
    client.mint_coin(liquidity_account.address, 10_000_000, currency_code="Coin1",auth_key_prefix=liquidity_account.auth_key_prefix,is_blocking=True)
    client.add_currency_to_account(liquidity_account, "Coin2")
    client.mint_coin(liquidity_account.address, 10_000_000, currency_code="Coin2",auth_key_prefix=liquidity_account.auth_key_prefix,is_blocking=True)

    swap_account = wallet.new_account()
    client.mint_coin(swap_account.address, 10_000_000, auth_key_prefix=swap_account.auth_key_prefix,is_blocking=True)
    client.add_currency_to_account(swap_account, "Coin1")
    client.mint_coin(swap_account.address, 10_000_000, currency_code="Coin1",auth_key_prefix=swap_account.auth_key_prefix,is_blocking=True)
    client.add_currency_to_account(swap_account, "Coin2")
    client.mint_coin(swap_account.address, 10_000_000, currency_code="Coin2",auth_key_prefix=swap_account.auth_key_prefix,is_blocking=True)

    client.swap_add_liquidity(liquidity_account, "LBR", "Coin1", 3243244, 4354435)
    client.swap_add_liquidity(liquidity_account, "Coin2", "Coin1", 4534452, 2443244)
    out, _ = client.swap_get_swap_input_amount("Coin2", "LBR", 243444)
    bb = client.get_balance(swap_account.address, "LBR")
    client.swap(swap_account, "Coin2", "LBR", out)
    ab = client.get_balance(swap_account.address, "LBR")
    assert ab - bb == 243444

def test_swap_get_liquidity_output_amount():
    wallet = Wallet.new()
    
    module_account = wallet.new_account()
    client.mint_coin(module_account.address, 10_000_000, auth_key_prefix=module_account.auth_key_prefix, is_blocking=True)
    client.swap_publish_contract(module_account)
    client.set_exchange_module_address(module_account.address)
    client.swap_initialize(module_account)
    client.swap_add_currency(module_account, "LBR")
    client.swap_add_currency(module_account, "Coin1")
    client.swap_add_currency(module_account, "Coin2")

    liquidity_account = wallet.new_account()
    client.mint_coin(liquidity_account.address, 10_000_000, auth_key_prefix=liquidity_account.auth_key_prefix, is_blocking=True)
    client.add_currency_to_account(liquidity_account, "Coin1")
    client.mint_coin(liquidity_account.address, 10_000_000, currency_code="Coin1",auth_key_prefix=liquidity_account.auth_key_prefix,is_blocking=True)
    client.add_currency_to_account(liquidity_account, "Coin2")
    client.mint_coin(liquidity_account.address, 10_000_000, currency_code="Coin2",auth_key_prefix=liquidity_account.auth_key_prefix,is_blocking=True)

    swap_account = wallet.new_account()
    client.mint_coin(swap_account.address, 10_000_000, auth_key_prefix=swap_account.auth_key_prefix,is_blocking=True)
    client.add_currency_to_account(swap_account, "Coin1")
    client.mint_coin(swap_account.address, 10_000_000, currency_code="Coin1",auth_key_prefix=swap_account.auth_key_prefix,is_blocking=True)
    client.add_currency_to_account(swap_account, "Coin2")
    client.mint_coin(swap_account.address, 10_000_000, currency_code="Coin2",auth_key_prefix=swap_account.auth_key_prefix,is_blocking=True)

    client.swap_add_liquidity(liquidity_account, "LBR", "Coin1", 3243243, 432432)
    out = client.swap_get_liquidity_output_amount("Coin1", "LBR", 243244)
    bc1b = client.get_balance(liquidity_account.address, "Coin1")
    client.swap_add_liquidity(liquidity_account, "LBR", "Coin1", out, 1000000000)
    ac1b = client.get_balance(liquidity_account.address, "Coin1")
    assert bc1b - ac1b == 243244


def test_get_currency_max_output_path():
    wallet = Wallet.new()
    
    module_account = wallet.new_account()
    client.mint_coin(module_account.address, 10_000_000, auth_key_prefix=module_account.auth_key_prefix, is_blocking=True)
    client.swap_publish_contract(module_account)
    client.set_exchange_module_address(module_account.address)
    client.swap_initialize(module_account)
    client.swap_add_currency(module_account, "LBR")
    client.swap_add_currency(module_account, "Coin1")
    client.swap_add_currency(module_account, "Coin2")

    liquidity_account = wallet.new_account()
    client.mint_coin(liquidity_account.address, 10_000_000, auth_key_prefix=liquidity_account.auth_key_prefix, is_blocking=True)
    client.add_currency_to_account(liquidity_account, "Coin1")
    client.mint_coin(liquidity_account.address, 10_000_000, currency_code="Coin1", auth_key_prefix=liquidity_account.auth_key_prefix, is_blocking=True)
    client.add_currency_to_account(liquidity_account, "Coin2")
    client.mint_coin(liquidity_account.address, 10_000_000, currency_code="Coin2", auth_key_prefix=liquidity_account.auth_key_prefix, is_blocking=True)

    swap_account = wallet.new_account()
    client.mint_coin(swap_account.address, 10_000_000, auth_key_prefix=swap_account.auth_key_prefix, is_blocking=True)
    client.add_currency_to_account(swap_account, "Coin1")
    client.mint_coin(swap_account.address, 10_000_000, currency_code="Coin1", auth_key_prefix=swap_account.auth_key_prefix, is_blocking=True)
    client.add_currency_to_account(swap_account, "Coin2")
    client.mint_coin(swap_account.address, 10_000_000, currency_code="Coin2", auth_key_prefix=swap_account.auth_key_prefix, is_blocking=True)

    client.swap_add_liquidity(liquidity_account, "LBR", "Coin1", 250_000, 100_000)
    client.swap_add_liquidity(liquidity_account, "Coin2", "Coin1", 200_000, 100_000)
    client.swap_add_liquidity(liquidity_account, "Coin2", "LBR", 100_000, 100_000)
    path = client.get_currency_max_output_path("Coin2", "LBR", 20000)
    assert path == [2, 1, 0]

def test_get_currency_min_input_path():
    wallet = Wallet.new()
    
    module_account = wallet.new_account()
    client.mint_coin(module_account.address, 10_000_000, auth_key_prefix=module_account.auth_key_prefix, is_blocking=True)
    client.swap_publish_contract(module_account)
    client.set_exchange_module_address(module_account.address)
    client.swap_initialize(module_account)
    client.swap_add_currency(module_account, "LBR")
    client.swap_add_currency(module_account, "Coin1")
    client.swap_add_currency(module_account, "Coin2")

    liquidity_account = wallet.new_account()
    client.mint_coin(liquidity_account.address, 10_000_000, auth_key_prefix=liquidity_account.auth_key_prefix, is_blocking=True)
    client.add_currency_to_account(liquidity_account, "Coin1")
    client.mint_coin(liquidity_account.address, 10_000_000, currency_code="Coin1", auth_key_prefix=liquidity_account.auth_key_prefix, is_blocking=True)
    client.add_currency_to_account(liquidity_account, "Coin2")
    client.mint_coin(liquidity_account.address, 10_000_000, currency_code="Coin2", auth_key_prefix=liquidity_account.auth_key_prefix, is_blocking=True)

    swap_account = wallet.new_account()
    client.mint_coin(swap_account.address, 10_000_000, auth_key_prefix=swap_account.auth_key_prefix, is_blocking=True)
    client.add_currency_to_account(swap_account, "Coin1")
    client.mint_coin(swap_account.address, 10_000_000, currency_code="Coin1", auth_key_prefix=swap_account.auth_key_prefix, is_blocking=True)
    client.add_currency_to_account(swap_account, "Coin2")
    client.mint_coin(swap_account.address, 10_000_000, currency_code="Coin2", auth_key_prefix=swap_account.auth_key_prefix, is_blocking=True)

    client.swap_add_liquidity(liquidity_account, "LBR", "Coin1", 250_000, 100_000)
    client.swap_add_liquidity(liquidity_account, "Coin2", "Coin1", 200_000, 100_000)
    client.swap_add_liquidity(liquidity_account, "Coin2", "LBR", 100_000, 100_000)
    path = client.get_currency_min_input_path("Coin2", "LBR", 20000)
    assert path == [2, 1, 0]



