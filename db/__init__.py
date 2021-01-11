import json
import psycopg2

TABLE_NAME = "liquidator"

def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    if type(obj) not in (list, dict, str, int, float, bool):
        if hasattr(obj, "__dataclass_fields__"):
            ret = {key: getattr(obj, key) for key in obj.__dataclass_fields__.keys()}
            return ret
        return obj.__dict__

class DBManager():
    def __init__(self, dsn):
        self._dsn = dsn

    def execute(self, cmd, data=None):
        conn = psycopg2.connect(self._dsn)
        cursor = conn.cursor()
        if data is None:
            cursor.execute(cmd)
        else:
            cursor.execute(cmd, (data,))
        conn.commit()
        conn.close()

    def query(self, cmd):
        conn = psycopg2.connect(self._dsn)
        cursor = conn.cursor()
        cursor.execute(cmd)
        result = cursor.fetchall()
        conn.close()
        return result


    def set(self, key, obj):
        if hasattr(obj, "__dataclass_fields__"):
            values = f"('{obj.get_key(key)}', '{json.dumps(obj.to_json())}')"
        else:
            values = f"('{key}', '{obj}')"
        sql = f'''
        INSERT INTO {TABLE_NAME} (key, value) VALUES {values} ON CONFLICT (key) DO UPDATE
        SET value=excluded.value
        '''
        self.execute(sql)

    def sets(self, d_values):
        if len(d_values) == 0:
            return
        values = ""
        i = 1
        for key, obj in d_values.items():
            i += 1
            if hasattr(obj, "__dataclass_fields__"):
                values += f"('{obj.get_key(key)}', '{json.dumps(obj.to_json())}'),"
            else:
                values += f"('{key}', '{obj}'),"
            if i % 100 == 0:
                values = values[:-1]
                sql = f'''
                INSERT INTO {TABLE_NAME} (key, value) VALUES {values} ON CONFLICT (key) DO UPDATE
                SET value=excluded.value
                '''
                self.execute(sql)
                values = ""
        if len(values):
            values = values[:-1]
            sql = f'''
            INSERT INTO {TABLE_NAME} (key, value) VALUES {values} ON CONFLICT (key) DO UPDATE
            SET value=excluded.value
            '''
            self.execute(sql)

    def get(self, key, obj_type, default_value=None):
        if hasattr(obj_type, "__dataclass_fields__"):
            sql = f"SELECT * FROM {TABLE_NAME} WHERE KEY = '{obj_type.get_key(key)}' "
            result = self.query(sql)
            if len(result):
                result = result[0][1]
                return obj_type.from_json(result)

        sql = f"SELECT * FROM {TABLE_NAME} WHERE KEY = '{key}' "
        result = self.query(sql)
        if len(result):
            return result[0][1]

        return default_value

    def gets(self, obj_type):
        sql = f"SELECT * FROM {TABLE_NAME} WHERE KEY LIKE '{obj_type.PREFIX}%' "
        result = self.query(sql)
        if len(result):
            return [obj_type.from_json(v[1]) for v in result]
        return []


