from lbrtypes.transaction.script import Script as LibraScript
from banktypes.bytecode import get_code

class Script(LibraScript):

    @staticmethod
    def gen_script(code_type, *args, ty_args=None, module_address=None):
        code = get_code(code_type, module_address)
        if ty_args is None:
            ty_args = []
        return Script(code, ty_args, list(args))