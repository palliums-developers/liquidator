from canoser import Struct, Uint64
from move_core_types.move_resource import MoveResource
from lbrtypes.account_config.constants import AccountAddress


class ParentVASP(Struct, MoveResource):
    MODULE_NAME = "VASP"
    STRUCT_NAME = "ParentVASP"

    _fields = [
        ("human_name", str),
        ("base_url", str),
        ("expiration_date", Uint64),
        ("compliance_public_key", bytes),
    ]


class ChildVASP(Struct, MoveResource):
    MODULE_NAME = "VASP"
    STRUCT_NAME = "ChildVASP"

    _fields = [
        ("parent_vasp_addr", AccountAddress)
    ]
