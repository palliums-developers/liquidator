import json
from db.base import Base
from .const import dsn

class AccountTable(Base):
    MAX_INSERT_NUM = 2
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_all_accounts(self):
        sql = "SELECT * FROM account"
        return self.query(sql)

    def keep_accounts(self, accounts):
        if len(accounts) == 0:
            return
        list_num = len(accounts) // self.MAX_INSERT_NUM
        account_list = [accounts[i*self.MAX_INSERT_NUM: (i+1)*self.MAX_INSERT_NUM] for i in range(list_num+1)]
        for accounts in account_list:
            values = ''
            if len(accounts):
                for account in accounts:
                    values += f'''('{account.get("address")}', '{json.dumps(account.get("lock_amounts"))}', '{json.dumps(account.get("borrow_amounts"))}', {account.get("health")}),'''
                values = values[:-1]
                sql = f'''
                INSERT INTO account (address, lock_amounts, borrow_amounts, health) VALUES {values} ON CONFLICT (address) DO UPDATE
                SET lock_amounts=excluded.lock_amounts, borrow_amounts=excluded.borrow_amounts, health=excluded.health;
                '''
                self.execute(sql)

if __name__ == "__main__":
    table = AccountTable(dsn=dsn)
    account1 = {
        "address":"683af760e02fbb78c737aec86b5ed992",
        "lock_amounts": {"USD": 1},
        "borrow_amounts": {"USD": 2},
        "health": 1.234231
    }
    account2 = {
        "address":"683af760e02fbb78c737aec86b5ed991",
        "lock_amounts": {"USD": 3},
        "borrow_amounts": {"USD": 4},
        "health": 1
    }
    account3 = {
        "address":"683af760e02fbb78c737aec86b5ed990",
        "lock_amounts": {"USD": 3},
        "borrow_amounts": {"USD": 4},
        "health": 1
    }
    table.keep_accounts([account1, account2, account3])
    print(table.get_all_accounts())



