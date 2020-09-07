from canoser import Struct, Uint8
from move_core_types.account_address import AccountAddress as Address
from lbrtypes.bytecode import get_code, CodeType

class Module(Struct):
    _fields = [
        ("code", bytes)
    ]

    def get_code(self):
        return self.code.hex()

    @staticmethod
    def gen_module(module_address, module_name=None):
        module_address = Address.normalize_to_bytes(module_address)
        code = get_code(CodeType.PUBLISH_MODULE, module_address)
        if module_name:
            if isinstance(module_name, str):
                module_name = module_name.encode()
            module_name = module_name.rjust(7, b"0")
            code = code.replace(b"Violas1", module_name)
        return Module(code)

