from canoser import Struct, RustOptional
from lbrtypes.transaction import Version
from lbrtypes.proof.definition import AccountStateProof
from lbrtypes.account_state import AccountState

class AccountStateBlob(Struct):
    _fields = [
        ("blob", AccountState)
    ]

    @classmethod
    def from_proto(cls, proto):
        ret = cls()
        if len(proto.blob) == 0:
            ret.blob = AccountState()
        else:
            ret.blob = AccountState.deserialize(proto.blob)
        return ret

class AccountStateWithProof(Struct):
    _fields = [
        ("version", Version),
        ("blob", AccountStateBlob),
        ("proof", AccountStateProof)
    ]

    def verify(self):
        pass

    def get_event_key_and_count_by_query_path(self):
        pass


