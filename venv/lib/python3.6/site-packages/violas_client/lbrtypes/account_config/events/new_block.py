from canoser import Struct, Uint64
from move_core_types.account_address import AccountAddress
from move_core_types.move_resource import MoveResource

class NewBlockEvent(Struct, MoveResource):
    MODULE_NAME = "LibraBlock"
    STRUCT_NAME = "NewBlockEvent"

    _fields = [
        ("round", Uint64),
        ("proposer", AccountAddress),
        ("previous_block_votes", [AccountAddress]),
        ("time_micro_seconds", Uint64),
    ]

    def get_round(self):
        return self.round

    def get_proser(self):
        return self.proposer.hex()

    def get_prorosed_time(self):
        return self.time_micro_seconds