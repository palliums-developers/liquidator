from canoser import Struct, Uint64, Optional, RustOptional
from lbrtypes.event import EventHandle
from move_core_types.move_resource import MoveResource
from lbrtypes.account_config.constants.account import ACCOUNT_MODULE_NAME
from lbrtypes.account_config.resources import KeyRotationCapabilityResourceOption, WithdrawCapabilityResourceOption

class AccountResource(Struct, MoveResource):

    MODULE_NAME = ACCOUNT_MODULE_NAME
    STRUCT_NAME = ACCOUNT_MODULE_NAME

    _fields = [
        ("authentication_key", bytes),
        ("withdrawal_capability", WithdrawCapabilityResourceOption),
        ("key_rotation_capability", KeyRotationCapabilityResourceOption),
        ("received_events", EventHandle),
        ("sent_events", EventHandle),
        ("sequence_number", Uint64),
        ("is_frozen", bool),
    ]


    def get_sequence_number(self):
        return self.sequence_number


