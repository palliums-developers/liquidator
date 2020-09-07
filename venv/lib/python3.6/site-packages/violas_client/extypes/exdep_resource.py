from canoser import Struct, Uint64, Uint8
from lbrtypes.account_config import WithdrawCapabilityResource
from lbrtypes.account_config import MoveResource

EXDEP_MODULE_NAME = "ExDep"

class BalanceResource(Struct, MoveResource):
    MODULE_NAME = EXDEP_MODULE_NAME
    STRUCT_NAME = "Balance"

    _fields = [
        ("value", Uint64)
    ]

class WithdrawCapability(Struct):
    _fields = [
        ("cap", WithdrawCapabilityResource)
    ]

class MintEvent(Struct):
    _fields = [
        ("coina", str),
        ("deposit_amounta", Uint64),
        ("coinb", str),
        ("deposit_amountb", Uint64),
        ("mint_amount", Uint64),
    ]

class BurnEvent(Struct):
    _fields = [
        ("coina", str),
        ("withdraw_amounta", Uint64),
        ("coinb", str),
        ("withdraw_amountb", Uint64),
        ("burn_amount", Uint64),
    ]

class SwapEvent(Struct):
    _fields = [
        ("input_name", str),
        ("input_amount", Uint64),
        ("output_name", str),
        ("output_amount", Uint64),
        ("data", bytes)
    ]

