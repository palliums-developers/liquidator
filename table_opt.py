from db.base import Base
from db.const import dsn

create_account_table_sql = '''
    CREATE TABLE IF NOT EXISTS account(
        address CHAR(32) NOT NULL PRIMARY KEY,
        lock_amounts jsonb,
        borrow_amounts jsonb,
        health FLOAT
    );
'''

create_token_table_sql = '''
    CREATE TABLE IF NOT EXISTS token(
        token VARCHAR NOT NULL PRIMARY KEY,
        info jsonb
    );
'''

create_heigh_table_sql = '''
    CREATE TABLE IF NOT EXISTS height(
        chain_id VARCHAR NOT NULL PRIMARY KEY,
        height INT 
    );
'''

drop_account_table_sql = '''
    DROP TABLE account
'''

drop_token_table_sql = '''
    DROP TABLE token
'''

drop_height_table_sql = '''
    DROP TABLE height
'''



def create_table():
    db_opt = Base(dsn)
    db_opt.execute(create_account_table_sql)
    db_opt.execute(create_token_table_sql)
    db_opt.execute(create_heigh_table_sql)

def drop_table():
    db_opt = Base(dsn)
    db_opt.execute(drop_account_table_sql)
    db_opt.execute(drop_token_table_sql)
    db_opt.execute(drop_height_table_sql)

if __name__ == "__main__":
    drop_table()
    create_table()

