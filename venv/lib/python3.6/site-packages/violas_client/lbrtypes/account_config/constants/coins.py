from lbrtypes.account_config.constants import from_currency_code_string, CORE_CODE_ADDRESS
from move_core_types.language_storage import StructTag, TypeTag

COIN1_NAME = "Coin1"
COIN2_NAME = "Coin2"

def coin1_type() ->TypeTag:
    return TypeTag("Struct", StructTag(
        CORE_CODE_ADDRESS,
        from_currency_code_string(COIN1_NAME),
        from_currency_code_string(COIN1_NAME),
        []
    ))