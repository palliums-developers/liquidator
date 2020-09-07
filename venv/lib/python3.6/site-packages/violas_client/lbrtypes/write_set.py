from canoser import RustEnum, Struct
from lbrtypes.access_path import AccessPath

class WriteOp(RustEnum):
    _enums = [
        ("Deletion", None),
        ("Value", bytes)
    ]

    def is_deletion(self):
        return self.Deletion


class WriteSetMut(Struct):
    _fields = [
        ("write_set", [(AccessPath, WriteOp)])
    ]

    def len(self):
        return len(self.write_set)

    def is_empty(self):
        return self.len() == 0

    def freeze(self):
        return WriteSet(self)


class WriteSet(WriteSetMut):
    pass