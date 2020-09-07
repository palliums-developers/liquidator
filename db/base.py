import psycopg2

class Base():
    def __init__(self, new_table=True, **kwargs):
        self._conn = psycopg2.connect(**kwargs)
        self._cur = self._conn.cursor()
        if new_table:
            self.delete_table()
        if not self.table_exist():
            self.create_table()

    def get(self, *args, ad=True, **kwargs):
        items = []
        kft = ",".join(["%s"]*len(args))
        for key, value in kwargs.items():
            items.append(key)
            items.append(value)
        if ad:
            ft = ' and '.join(['%s=%s']*len(kwargs))
        else:
            ft = ' or '.join(['%s=%s']*len(kwargs))
        sql =self._cur.mogrify(f"select {kft} from %s where {ft}", (*args, *items))
        return self.select(sql)
    
    def insert(self, conkey=None, **kwargs):
        keys = ','.join(kwargs.keys())
        vft = ','.join(['%s']*len(kwargs))
        if conkey is None:
            sql =self._cur.mogrify(f"insert into {self.table_name} ({keys}) values ({vft})", (*kwargs.values(),))
        else:
            pft = ",".join(['%s=%s']*len(kwargs))
            items = []
            for key, value in kwargs.items():
                items.append(key)
                items.append(value)
            sql =self._cur.mogrify(f"insert into {self.table_name} ({keys}) values {vft} on conflict({conkey}) do update set {pft}", (*kwargs.values(), *items))
        return self.execute(sql)

    def update(self, primary_key, **kwargs):
        pft = ",".join(['%s=%s'] * len(kwargs))
        items = []
        for key, value in kwargs.items():
            items.append(key)
            items.append(value)
        sql = self._cur.mogrify(f"update {self.table_name} set {pft} where {self.primary_key} = %s", (*items, primary_key))
        return self.execute(sql)

    def add_array_element(self, primary_key, **kwargs):
        pft = ",".join(['%s= %s || %s'] * len(kwargs))
        items = []
        for key, value in kwargs.items():
            items.append(key)
            items.append(key)
            items.append(value)
        sql = self._cur.mogrify(f"update {self.table_name} set {pft} where {self.primary_key}=%s", (*items, primary_key))
        return self.execute(sql)

    def delete_array_element(self, primary_key, **kwargs):
        pft = ",".join(['%s=array_remove(%s,%s)'] * len(kwargs))
        items = []
        for key, value in kwargs.items():
            items.append(key)
            items.append(key)
            items.append(value)
        sql = self._cur.mogrify(f"update {self.table_name} set {pft} where {self.primary_key}=%s", (*items, primary_key))
        return self.execute(sql)

    def try_except(self):
        def wrapper(*args, **kwargs):
            # try:
                return self(*args, **kwargs)
            # except psycopg2.Error as e:
            #     print("get error:", e)
        return wrapper

    @try_except
    def select(self, sql):
        self._conn.execute(sql)
        return self._cur.fetchall()

    def execute(self, sql):
        self.common(sql)

    def execute_and_get_field(self, sql, field):
        try:
            self._cur.execute(sql + " RETURNING " + field)
        except Exception as e:
            self._conn.rollback()
            self._cur.execute(sql + " RETURNING " + field)
        self._conn.commit()

        return self._cur.fetchone()

    def execute_and_get_fields(self, sql, fields):
        try:
            self._cur.execute(sql + " RETURNING " + ",".join(fields))
        except Exception as e:
            self._conn.rollback()
            self._cur.execute(sql + " RETURNING " + ",".join(fields))
        self._conn.commit()
        return self._cur.fetchone()


    def execute_many(self, sqls):
        return self.common_many(sqls)


    @try_except
    def close(self):
        self._cur.close()
        self._conn.close()

    '''.....................called internal.............................'''

    @try_except
    def common(self, sql):
        try:
            self._cur.execute(sql)
        except:
            self._conn.rollback()
            self._cur.execute(sql)
        self._conn.commit()

    @try_except
    def common_many(self, sqls):
        try:
            self._cur.execute_many(sqls)
        except:
            self._conn.rollback()
            self._cur.execute_many(sqls)
        self._conn.commit()

    def create_table(self):
        raise NotImplementedError

    def delete_table(self):
        sql = f"drop table if exists {self.table_name}"
        self.common(sql)

    @try_except
    def table_exist(self):
        sql = f"select count(*) from pg_class where relname = '{self.table_name}'"
        self._cur.execute(sql)
        return self._cur.fetchone()[0]



if __name__ == "__main__":
    db = Base(user="root", dbname="postgres")

