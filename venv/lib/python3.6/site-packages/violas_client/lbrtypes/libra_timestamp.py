from canoser import Struct, Uint64
from move_core_types.move_resource import MoveResource

class LibraTimestamp(Struct):
    _fields = [
        ("microseconds", Uint64)
    ]

class LibraTimestampResource(Struct, MoveResource):
    MODULE_NAME = "LibraTimestamp"
    STRUCT_NAME = "CurrentTimeMicroseconds"

    _fields = [
        ("libra_timestamp", LibraTimestamp)
    ]