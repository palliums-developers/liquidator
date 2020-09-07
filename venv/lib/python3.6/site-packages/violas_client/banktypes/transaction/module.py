from lbrtypes.transaction.module import Module as LibraModule
from move_core_types.account_address import AccountAddress as Address
from banktypes.bytecode import get_code, CodeType

class Module(LibraModule):
    @staticmethod
    def gen_module(module_address=None):
        code = get_code(CodeType.BANK, module_address)
        return Module(code)