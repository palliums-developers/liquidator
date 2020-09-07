from canoser import RustEnum, Uint64, Uint8, Uint128
from move_core_types.account_address import AccountAddress
from crypto.ed25519 import ED25519_PUBLIC_KEY_LENGTH

def normalize_public_key(public_key):
    if isinstance(public_key, list):
        if len(public_key) != ED25519_PUBLIC_KEY_LENGTH:
            raise ValueError(f"{public_key} is not a valid public_key.")
        return bytes(list)
    if isinstance(public_key, bytes):
        if len(public_key) != ED25519_PUBLIC_KEY_LENGTH:
            raise ValueError(f"{public_key} is not a valid public_key.")
        return public_key
    if isinstance(public_key, str):
        if len(public_key) != ED25519_PUBLIC_KEY_LENGTH*2:
            raise ValueError(f"{public_key} is not a valid public_key.")
        return bytes.fromhex(public_key)

class TransactionArgument(RustEnum):
    _enums = [
        ("U8", Uint8),
        ("U64", Uint64),
        ("U128", Uint128),
        ("Address", AccountAddress),
        ("U8Vector", bytes),
        ("Bool", bool),
    ]

    @classmethod
    def to_address(cls, value):
        if value is None:
            value = b""
        address = AccountAddress.normalize_to_bytes(value)
        return cls("Address", address)

    @classmethod
    def to_U64(cls, u64):
        return cls("U64", u64)

    @classmethod
    def to_U8Vector(cls, value, hex=True):
        if value is None:
            value = b""
        if isinstance(value, str):
            if not hex:
                value = str.encode(value)
            else:
                value = bytes.fromhex(value)

        return cls("U8Vector", value)

    @classmethod
    def to_bool(cls, value):
        return cls("Bool", value)
