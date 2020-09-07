from move_core_types.language_storage import ModuleId, CORE_CODE_ADDRESS

ACCOUNT_LIMITS_MODULE_NAME = "AccountLimits"
ACCOUNT_LIMITS_MODULE = ModuleId(CORE_CODE_ADDRESS, ACCOUNT_LIMITS_MODULE_NAME)
ACCOUNT_LIMITS_WINDOW_STRUCT_NAME = "Window"

def account_limits_module_name():
    return ACCOUNT_LIMITS_MODULE

def account_limits_window_struct_name():
    return ACCOUNT_LIMITS_WINDOW_STRUCT_NAME