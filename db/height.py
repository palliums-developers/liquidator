import json
from db.base import Base
from .const import dsn

class HeightTable(Base):
    MAX_INSERT_NUM = 2
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_height(self):
        sql = "SELECT * FROM height"
        ret = self.query(sql)
        if len(ret) > 0:
            return ret[0][1]
        return 0

    def set_height(self, height):
        sql = f'''
        INSERT INTO height (chain_id, height) VALUES ('testnet', {height}) ON CONFLICT (chain_id) DO UPDATE
        SET height=excluded.height;
        '''
        self.execute(sql)

if __name__ == "__main__":
    table = HeightTable(dsn=dsn)
    height = 10
    table.set_height(height)
    print(table.get_height())


