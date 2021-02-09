import json
import dataclasses

def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    if type(obj) not in (list, dict, str, int, float, bool):
        if hasattr(obj, "__dataclass_fields__"):
            ret = {key: getattr(obj, key) for key in obj.__dataclass_fields__.keys()}
            return ret
        return obj.__dict__


@dataclasses.dataclass
class Base:
    PREFIX = ""

    def to_json(self):
        return json.loads(json.dumps(self, default=set_default, indent=4))

    @classmethod
    def from_json(cls, json):
        params = {}
        for key, type in cls.__dataclass_fields__.items():
            value = json.get(key)
            type = type.type
            if hasattr(type, "__dataclass_fields__"):
                params[key] = type.from_json(value)
            else:
                params[key] = value
        return cls(**params)

    @classmethod
    def get_key(cls, key):
        return cls.PREFIX + key

