'''
    扫链服务
'''
import time
import traceback
from queue import Queue
from threading import Thread
from bank import Bank
from coin_porter import CoinPorter
from violas_client.lbrtypes.bytecode import CodeType
from network import create_violas_client

class ScannerThread(Thread):

    UPDATING = 0
    UPDATED = 1

    def __init__(self, queue: Queue):
        super(ScannerThread, self).__init__()
        self.client = create_violas_client()
        self.queue = queue
        self.state = self.UPDATING
        self.bank = Bank()
        self.coin_porter = CoinPorter()

    def run(self):
        limit = 1000
        self.bank.update_from_db()
        self.coin_porter.update_from_db()
        db_height = self.bank.height

        while True:
            # try:
                txs = self.client.get_transactions(self.bank.height, limit)
                if len(txs) == 0:
                    time.sleep(1)
                    continue
                for index, tx in enumerate(txs):
                    if tx.get_code_type() == CodeType.UNKNOWN:
                        continue
                    if tx.get_code_type() != CodeType.BLOCK_METADATA and tx.is_successful():
                        addrs = self.bank.add_tx(tx)
                        if addrs is not None:
                            v = tx.get_version()
                            self.check_token(v)
                        if self.state == self.UPDATED:
                            if addrs is not None:
                                for addr in addrs:
                                    self.queue.put(addr)

                        if self.state == self.UPDATING:
                            self.coin_porter.add_tx(tx)

                self.bank.height += len(txs)
                if self.state == self.UPDATING and len(txs) < limit:
                    self.state = self.UPDATED
                if self.bank.height - db_height >= 10000000_000:
                    self.bank.update_to_db()
                    self.coin_porter.update_to_db()
                    print(self.bank.height)
                    db_height = self.bank.height
            # except Exception as e:
            #     print("scan_thread")
            #     traceback.print_exc()
            #     time.sleep(2)

    def check_token(self, version):
        token_infos = self.client.get_account_state(self.client.get_bank_owner_address(), version).get_token_info_store_resource(
            accrue_interest=False).tokens
        currencies = self.client.bank_get_registered_currencies(True)
        for currency in currencies:
            index = self.client.bank_get_currency_index(currency_code=currency)
            currency_info = token_infos[index: index + 2]
            contract_value = self.client.bank_get_amount(self.client.BANK_OWNER_ADDRESS, currency)
            self.assert_token_consistence(currency, currency_info, contract_value)

    def assert_token_consistence(self, currency, token_infos, contract_value):
        # print(f"checkout {currency}")
        local_info = self.bank.get_token_info(currency)
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
        assert contract_value == local_info.contract_value
