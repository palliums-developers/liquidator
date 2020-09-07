from canoser import Struct
from move_core_types.language_storage import TypeTag
from lbrtypes.transaction.transaction_argument import TransactionArgument
from lbrtypes.bytecode import get_code_type, get_code

SCRIPT_HASH_LENGTH = 32

class Script(Struct):
    _fields = [
        ("code", bytes),
        ("ty_args", [TypeTag]),
        ("args", [TransactionArgument]),
    ]

    def get_code_type(self):
        return get_code_type(self.code)

    def get_code(self):
        return self.code.hex()

    def get_ty_args(self):
        return self.ty_args

    def get_args(self):
        return self.args

    @staticmethod
    def gen_script(code_type, *args, ty_args=None, currency_module_address=None):
        code = get_code(code_type, currency_module_address)
        if ty_args is None:
            ty_args = []
        return Script(code, ty_args, list(args))

