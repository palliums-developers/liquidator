from move_core_types.language_storage import ModuleId, StructTag, TypeTag, CORE_CODE_ADDRESS
from canoser import Struct, Uint64
from move_core_types.account_address import AccountAddress

ACCOUNT_ROLE_MODULE_NAME = "LibraAccount"
ACCOUNT_ROLE_MODULE = ModuleId(CORE_CODE_ADDRESS, ACCOUNT_ROLE_MODULE_NAME)
ACCOUNT_ROLE_STRUCT_NAME = "Role"

VASP_TYPE_MODULE_NAME = "VASP"
VASP_TYPE_MODULE = ModuleId(CORE_CODE_ADDRESS, VASP_TYPE_MODULE_NAME)
ROOT_VASP_STRUCT_NAME = "RootVASP"

EMPTY_ACCOUNT_ROLE_MODULE_NAME = "Empty"
EMPTY_ACCOUNT_ROLE_MODULE = ModuleId(CORE_CODE_ADDRESS, EMPTY_ACCOUNT_ROLE_MODULE_NAME)
EMPTY_ACCOUNT_STRUCT_NAME = "Empty"

UNHOSTED_TYPE_MODULE_NAME = "Unhosted"
UNHOSTED_TYPE_MODULE = ModuleId(CORE_CODE_ADDRESS, UNHOSTED_TYPE_MODULE_NAME)
UNHOSTED_STRUCT_NAME = "Unhosted"

def account_role_module_name():
    return ACCOUNT_ROLE_MODULE_NAME

def account_role_struct_name():
    return ACCOUNT_ROLE_STRUCT_NAME

def vasp_type_module_name():
    return VASP_TYPE_MODULE_NAME

def root_vasp_type_struct_name():
    return ROOT_VASP_STRUCT_NAME

def empty_account_role_module_name():
    return EMPTY_ACCOUNT_ROLE_MODULE_NAME

def empty_account_role_struct_name():
    return EMPTY_ACCOUNT_STRUCT_NAME

def unhosted_type_module_name():
    return UNHOSTED_TYPE_MODULE_NAME

def unhosted_type_struct_name():
    return UNHOSTED_STRUCT_NAME


def empty_account_role_struct_tag() -> StructTag:
        inner_struct_tag = StructTag(
            CORE_CODE_ADDRESS,
            empty_account_role_module_name(),
            empty_account_role_struct_name(),
            [],
        )
        return StructTag(
            CORE_CODE_ADDRESS,
            account_role_module_name(),
            account_role_struct_name(),
            [TypeTag("Struct", inner_struct_tag)],

        )

def vasp_account_type_struct_tag() -> StructTag :
    inner_struct_tag = StructTag(
        CORE_CODE_ADDRESS,
        vasp_type_module_name(),
        root_vasp_type_struct_name(),
        [],

    )

    return StructTag(
        CORE_CODE_ADDRESS,
        account_role_module_name(),
        account_role_struct_name(),
        [TypeTag("Struct", inner_struct_tag)],
    )

def unhosted_account_type_struct_tag() -> StructTag :
    inner_struct_tag = StructTag(
        CORE_CODE_ADDRESS,
        unhosted_type_module_name(),
        unhosted_type_struct_name(),
        [],
    )
    return StructTag(
        CORE_CODE_ADDRESS,
        account_role_module_name(),
        account_role_struct_name(),
        [TypeTag("Struct", inner_struct_tag)]
    )

