from canoser import Struct
from lbrtypes.contract_event import ContractEvent
from lbrtypes.write_set import WriteSet

class ChangeSet(Struct):
    _fields = [
        ("write_set", WriteSet),
        ("events", [ContractEvent])
    ]
