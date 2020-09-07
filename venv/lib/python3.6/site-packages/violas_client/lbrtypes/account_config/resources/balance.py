from canoser import Struct, Uint64
from move_core_types.move_resource import MoveResource
from move_core_types.language_storage import StructTag, CORE_CODE_ADDRESS
from lbrtypes.access_path import AccessPath
from lbrtypes.account_config.constants.account import ACCOUNT_MODULE_NAME

class BalanceResource(Struct, MoveResource):
    MODULE_NAME = ACCOUNT_MODULE_NAME
    STRUCT_NAME = "Balance"

    _fields = [
        ("coin", Uint64)
    ]

    def get_coin(self):
        return self.coin

    @classmethod
    def struct_tag_for_currency(cls, current_typetag):
        return StructTag(
            CORE_CODE_ADDRESS,
            cls.module_identifier(),
            cls.struct_identifier(),
            [current_typetag]
        )

    @classmethod
    def access_path_for(cls, currency_typetag):
        from lbrtypes.access_path import Accesses
        return AccessPath.resource_access_vec(cls.struct_tag_for_currency(currency_typetag), Accesses.empty())

    # @classmethod
    # def type_params(cls):
    #     return [lbr_type_tag()]