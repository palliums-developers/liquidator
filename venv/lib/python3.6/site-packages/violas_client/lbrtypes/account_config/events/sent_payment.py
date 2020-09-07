from canoser import Struct, Uint64
from move_core_types.identifier import Identifier
from move_core_types.account_address import AccountAddress
from move_core_types.move_resource import MoveResource
from lbrtypes.account_config.constants.libra import LIBRA_MODULE_NAME
from lbrtypes.account_config.resources.account import AccountResource


ACCOUNT_SENT_EVENT_PATH = AccountResource.resource_path() + b"/sent_events_count/"

class SentPaymentEvent(Struct, MoveResource):
    MODULE_NAME = LIBRA_MODULE_NAME
    STRUCT_NAME = "SentPaymentEvent"

    _fields = [
        ("amount", Uint64),
        ("currency_code", Identifier),
        ("receiver", AccountAddress),
        ("metadata", bytes),
    ]