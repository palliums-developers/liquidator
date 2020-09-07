from db.base import Base

class Currency(Base):
    def __init__(self, **kwargs):
        self.table_name = "currency"
        self.primary_key = "currency_code"
        super().__init__(**kwargs)

    def create_table(self):
        sql = f'''create table {self.table_name}(
            currency_code varchar PRIMARY KEY ,
            lock_accounts text[],
            borrow_accounts text[],
            price integer 
        )'''
        self.common(sql)

    def add_currency(self, currency_code):
        return self.insert(currency_code=currency_code, lock_accounts=[], borrow_accounts=[], price=0)

    def update_price(self, currency_code, price):
        return self.update(currency_code, price=price)

    def add_lock_account(self, currency_code, account):
        return self.add_array_element(currency_code, lock_accounts=account)

    def add_borrow_account(self, currency_code, account):
        return self.add_array_element(currency_code, borrow_accounts=account)

    def delete_lock_account(self, currency_code, account):
        return self.delete_array_element(currency_code, lock_accounts=account)

    def delete_borrow_account(self, currency_code, account):
        return self.delete_array_element(currency_code, borrow_accounts=account)

    def get_all_accounts(self, currency_code):
        lock_accounts, borrow_accounts = self.get("lock_accounts", "borrow_accounts", currency_code=currency_code)
        return list(set(lock_accounts) | set(borrow_accounts))


if __name__ == "__main__":
    db = Currency(user="root", dbname="postgres", new_table=True)
    db.add_currency("Coin1")