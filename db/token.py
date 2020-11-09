import json
from db.base import Base
from .const import dsn

class TokenTable(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_all_tokens(self):
        sql = "SELECT * FROM token"
        return self.query(sql)

    def keep_tokens(self, tokens):
        if len(tokens) == 0:
            return
        values = ''
        for token in tokens:
            values += f'''('{token.get("token")}', '{json.dumps(token.get("info"))}'),'''
        values = values[:-1]

        sql = f'''
        INSERT INTO token (token, info) VALUES {values} ON CONFLICT (token) DO UPDATE
        SET info=excluded.info;
        '''
        self.execute(sql)

if __name__ == "__main__":
    table = TokenTable(dsn=dsn)
    token = {
        "token":"token1",
        "info": {"1":1}
    }
    table.keep_tokens([token])
    print(table.get_all_tokens())




