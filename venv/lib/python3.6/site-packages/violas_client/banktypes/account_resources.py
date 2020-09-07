from canoser import Struct, Uint64
from lbrtypes.event import EventHandle
from move_core_types.account_address import AccountAddress
from move_core_types.move_resource import MoveResource

class LibraTokenResource(Struct, MoveResource):
    MODULE_NAME = "ViolasBank"
    STRUCT_NAME = "LibraToken"

    _fields = [
        ("coin", Uint64),
        ("index", Uint64)
    ]

    def get_libra_amount(self):
        return self.coin.value

    def get_index(self):
        return self.index

class BankResource(Struct):

    _fields = [
        ("index", Uint64),
        ("value", Uint64)
    ]

    def get_index(self):
        return self.index

    def get_value(self):
        return self.value

class BorrowInfoResource(Struct):
    _fields = [
        ("principal", Uint64),
        ("interest_index", Uint64)
    ]

    def get_principal(self):
        return self.principal

    def get_interest_index(self):
        return self.interest_index

class TokensResource(Struct, MoveResource):
    MODULE_NAME = "ViolasBank"
    STRUCT_NAME = "Tokens"

    _fields = [
        # index 代表进入银行的钱. index+1代表存入银行的钱
        ("ts", [BankResource]),
        ("borrows", [BorrowInfoResource])
    ]


class OrderResource(Struct):

    _fields = [
        ("t", BankResource),
        ("peer_token_idx", Uint64),
        ("peer_token_amount", Uint64)
    ]

class UserInfoResource(Struct, MoveResource):
    MODULE_NAME = "ViolasBank"
    STRUCT_NAME = "UserInfo"

    _fields = [
        ("violas_events", EventHandle),
        ("data", str),
        ("orders", [OrderResource]),
        ("order_freeslots", [Uint64]),
        ("debug", str)
    ]

class TokenInfoResource(Struct):
    _fields = [
        ("currency_code", str),
        ("owner", AccountAddress),
        ("total_supply", Uint64),
        ("total_reserves", Uint64),
        ("total_borrows", Uint64),
        ("borrow_index", Uint64),
        ("price", Uint64),
        ("price_oracle", AccountAddress),
        ("collateral_factor", Uint64),
        ("base_rate", Uint64),
        ("rate_multiplier", Uint64),
        ("rate_jump_multiplier", Uint64),
        ("rate_kink", Uint64),
        ("last_minute", Uint64),
        ("data", str),
        ("bulletin_first", str),
        ("bulletins", [str]),
    ]

class TokenInfoStoreResource(Struct, MoveResource):
    MODULE_NAME = "ViolasBank"
    STRUCT_NAME = "TokenInfoStore"

    _fields = [
        ("supervisor", AccountAddress),
        ("tokens", [TokenInfoResource])
    ]

class EventPublish(Struct):
    _fields = [
        ("data", bytes)
    ]

class EventRegisterLibraToken(Struct):
    _fields = [
        ("currency_code", str),
        ("price_oracle", AccountAddress),
        ("collateral_factor", Uint64),
        ("base_rate", Uint64),
        ("rate_multiplier", Uint64),
        ("rate_jump_multiplier", Uint64),
        ("rate_kink", Uint64),
        ("data", bytes)
    ]

class EventMint(Struct):
    _fields = [
        ("tokenidx", Uint64),
        ("payee", AccountAddress),
        ("amount", Uint64),
        ("data", bytes),
    ]

class EventTransfer(Struct):
    _fields = [
        ("tokenidx", Uint64),
        ("payee", AccountAddress),
        ("amount", Uint64),
        ("data", bytes),
    ]

class EventUpdatePrice (Struct):
    _fields = [
        ("currency_code", str),
        ("tokenidx", Uint64),
        ("price", Uint64),
    ]

class EventLock(Struct):
    _fields = [
        ("currency_code", str),
        ("tokenidx", Uint64),
        ("amount", Uint64),
        ("data", bytes),
    ]

class EventRedeem (Struct):
    _fields = [
        ("currency_code", str),
        ("tokenidx", Uint64),
        ("amount", Uint64),
        ("data", bytes),
    ]

class EventBorrow (Struct):
    _fields = [
        ("currency_code", str),
        ("tokenidx", Uint64),
        ("amount", Uint64),
        ("data", bytes),
    ]

class EventRepayBorrow (Struct):
    _fields = [
        ("currency_code", str),
        ("tokenidx", Uint64),
        ("amount", Uint64),
        ("data", bytes),
    ]

class EventLiquidateBorrow (Struct):
    _fields = [
        ("currency_code1", str),
        ("currency_code2", str),
        ("tokenidx", Uint64),
        ("borrower", AccountAddress),
        ("amount", Uint64),
        ("collateral_tokenidx", Uint64),
        ("data", bytes),
    ]

class EventUpdateCollateralFactor (Struct):
    _fields = [
        ("currency_code", str),
        ("tokenidx", Uint64),
        ("factor", Uint64),
    ]

class EventEnterBank (Struct):
    _fields = [
        ("currency_code", str),
        ("tokenidx", Uint64),
        ("amount", Uint64),
    ]

class EventExitBank (Struct):
    _fields = [
        ("currency_code", str),
        ("tokenidx", Uint64),
        ("amount", Uint64),
    ]


event_type_map = {
    "0": EventPublish,
    "1": EventRegisterLibraToken,
    "6": EventUpdatePrice,
    "7": EventLock,
    "8": EventRedeem,
    "9": EventBorrow,
    "10": EventRepayBorrow,
    "11": EventLiquidateBorrow,
    "12": EventUpdateCollateralFactor,
    "13": EventEnterBank,
    "14": EventExitBank,
}


class ViolasEvent(Struct):
    _fields = [
        ("etype", Uint64),
        ("paras", bytes),
        ("data", bytes),
    ]

    def get_bank_event(self):
        if not hasattr(self, "bank_event"):
            etype = str(self.etype)
            self.bank_event = event_type_map[etype].deserialize(self.paras)
        return self.bank_event

    def get_currency_code(self):
        if hasattr(self.get_bank_event(), "currency_code"):
            return self.get_bank_event().currency_code

    def get_amount(self):
        if hasattr(self.get_bank_event(), "amount"):
            return self.get_bank_event().amount

    def get_data(self):
        if hasattr(self.get_bank_event(), "data"):
            return self.get_bank_event().data.hex()
