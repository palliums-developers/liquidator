import sys
from db.base import Base

class Account(Base):
    def __init__(self, **kwargs):
        self.table_name = "account"
        self.primary_key = "account"
        super().__init__(**kwargs)

    def create_table(self):
        sql = f'''create table {self.table_name}(
            account varchar PRIMARY KEY ,
            lock_amounts json ,
            borrow_amounts json ,
            expiration_time integer ,
        )'''
        self.common(sql)

    def add_account(self, account):
        return self.insert(account=account, lock_amounts={}, borrow_amounts={}, expiration_time=-1)

    def update_lock_amounts(self, account, lock_amounts, expiration_time=sys.maxsize):
        return self.update(account, lock_amounts=lock_amounts, expiration_time=expiration_time)

    def update_borrow_amounts(self, account, borrow_amounts, expiration_time=sys.maxsize):
        return self.update(account, borrow_amounts=borrow_amounts, expiration_time=expiration_time)

    def get_account(self, account):
        return self.get("lock_amounts", "borrow_amounts", "expiration_time", account)

    def get_expiration_accounts(self, deadline):
        sql = f"select * from account where expiration_time <= {deadline}"
        return self.common(sql)

if __name__ == "__main__":
    db = Account(user="root", dbname="postgres")