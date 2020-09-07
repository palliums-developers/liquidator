from canoser import Struct, Uint8, RustEnum
from move_core_types.gas_schedule import CostTable, GasConstants
from lbrtypes.on_chain_config import OnChainConfig

class VMPublishingOption(RustEnum):
    _enums = [
        ("Locked", [bytes]),
        ("CustomScripts", None),
        ("Open", None)
    ]

class VMConfig(Struct, OnChainConfig):
    IDENTIFIER = "LibraVMConfig"

    _fields = [
        ("publishing_option", VMPublishingOption),
        ("gas_schedule", CostTable)
    ]

class CostTableInner(Struct):
    _fields = [
        ("instruction_table", bytes),
        ("native_table", bytes),
        ("gas_constants", GasConstants),
    ]

class VMConfigInner(Struct):
    _fields = [
        ("publishing_option", bytes),
        ("gas_schedule", CostTableInner)
    ]