from canoser import Struct, Uint64
from move_core_types.account_address import AccountAddress
from lbrtypes.event import EventHandle
from crypto.hash import HashValue
from move_core_types.move_resource import MoveResource

class BlockMetadata(Struct):
    _fields = [
        ("id", HashValue),
        ("round", Uint64),
        ("timestamp_usecs", Uint64),
        ("previous_block_votes", [AccountAddress]),
        ("proposer", AccountAddress),
    ]

    def get_id(self):
        return self.id.hex()

    def get_round(self):
        return self.round

    def get_timestamp_usecs(self):
        return self.timestamp_usecs

    def get_previous_block_votes(self):
        return [vote.hex() for vote in self.previous_block_votes]

    def get_proposer(self):
        return self.proposer.hex()

class LibraBlockResource(Struct, MoveResource):
    MODULE_NAME = "LibraBlock"
    STRUCT_NAME = "BlockMetadata"
    _fields = [
        ("height", Uint64),
        ("new_block_events", EventHandle)
    ]

NEW_BLOCK_EVENT_PATH = LibraBlockResource.resource_path() + b"/new_block_event/"

class LibraBlockResource(Struct, MoveResource):
    MODULE_NAME = "LibraBlock"
    STRUCT_NAME = "BlockMetadata"

    _fields = [
        ("height", Uint64),
        ("new_block_events", EventHandle)
    ]

    def get_height(self):
        return self.height

    def get_new_block_events(self):
        return self.new_block_events

class NewBlockEvent(Struct):
    _fields = [
        ("round", Uint64),
        ("proposer", AccountAddress),
        ("votes", [AccountAddress]),
        ("timestamp", Uint64),
    ]

    def get_round(self):
        return self.round

    def get_proposer(self):
        return self.proposer.hex()

    def get_votes(self):
        return [vote.hex() for vote in self.votes]

    def get_timestamp(self):
        return self.timestamp


