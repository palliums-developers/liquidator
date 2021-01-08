from network import create_database_manager
from db import TABLE_NAME

create_table_sql = f'''
    CREATE TABLE IF NOT EXISTS {TABLE_NAME }(
        key VARCHAR NOT NULL PRIMARY KEY,
        value jsonb 
    );
'''

drop_table_sql = f'''
    DROP TABLE {TABLE_NAME}
'''


def create_table():
    db_opt = create_database_manager()
    db_opt.execute(create_table_sql)

def drop_table():
    db_opt = create_database_manager()
    db_opt.execute(drop_table_sql)

if __name__ == "__main__":
    drop_table()
    create_table()

