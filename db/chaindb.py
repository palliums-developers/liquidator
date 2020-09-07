import time
from db.currency import Currency
from db.account import Account
from violas_client.vlstypes.view import TransactionView
from violas_client.banktypes.bytecode import CodeType

class ChainDB():
    def __init__(self, **kwargs):
        self.currencies = Currency(**kwargs)
        self.accounts = Account(**kwargs)

    def add_txs(self, txs):
        for tx in txs:
            self.add_tx(tx)

    def add_tx(self, tx:TransactionView):
        if not tx.is_successful():
            return
        if tx.get_code_type() == CodeType.BORROW:
            return self.add_borrow_tx(tx)
        if tx.get_code_type() == CodeType.LOCK:
            return self.add_lock_tx(tx)
        if tx.get_code_type() == CodeType.REDEEM:
            return self.add_redeem_tx(tx)
        if tx.get_code_type() == CodeType.REPAY_BORROW:
            return self.add_repay_borrow_tx(tx)
        if tx.get_code_type() == CodeType.UPDATE_PRICE:
            return self.add_update_price_tx(tx)

    def get_expiration_account(self):
        cur_time = time.time()
        return self.accounts.get_expiration_accounts(cur_time)

    '''.............called internal..................'''
    def add_borrow_tx(self, tx):
        sender = tx.get_sender()
        currency_code = tx.get_currency_code()
        amount = tx.get_amount()
        lock_amounts, borrow_amounts = self.accounts.get_account(sender)

    def add_lock_tx(self, tx):
        pass

    def add_redeem_tx(self):
        pass

    def add_repay_borrow_tx(self):
        pass

    def add_update_price_tx(self):
        pass


