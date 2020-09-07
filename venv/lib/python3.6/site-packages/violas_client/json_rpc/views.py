from typing import List
from canoser import Struct, Uint64, BoolT, StrT, RustEnum
from lbrtypes.account_state import AccountState
from lbrtypes.bytecode import get_code_type, CodeType

class AmountView(Struct):
    _fields = [
        ("amount", Uint64),
        ("currency", StrT)
    ]

class ParentVASPView(Struct):
    _fields = [
        ("human_name", str),
        ("base_url", str),
        ("expiration_time", Uint64),
        ("compliance_key", str),
        ("num_children", Uint64),
    ]

class AccountRoleView(RustEnum):
    _enums = [
        ("unknown", None),
        ("unhosted", None),
        ("empty", None),
        ("child_vasp", str),
        ("parent_vasp", ParentVASPView),
    ]

    @classmethod
    def from_value(cls, value):
        if value == "unknown":
            return cls("unknown", None)
        if value == "unhosted":
            return cls("unhosted", None)
        if value == "empty":
            return cls("empty", None)
        if value.get("child_vasp") is not None:
            return cls("child_vasp", value.get("child_vasp"))
        if value.get("parent_vasp") is not None:
            return cls("parent_vasp", ParentVASPView.from_value(value.get("parent_vasp")))

class AccountView(Struct):
    _fields = [
        ("balances", [AmountView]),
        ("sequence_number", Uint64),
        ("authentication_key", StrT),
        ("sent_events_key", StrT),
        ("received_events_key", StrT),
        ("delegated_key_rotation_capability", BoolT),
        ("delegated_withdrawal_capability", BoolT),
        ("is_frozen", BoolT),
        ("role", AccountRoleView),
    ]

    @staticmethod
    def from_response(response):
        #TODO:
        return response.value.value

    def get_balance(self, currency_code="LBR"):
        for item in self.balances:
            if item.currency == currency_code:
                return item.amount
        return 0

    def get_sequence_number(self):
        return self.sequence_number

    def get_authentication_key(self):
        return self.authentication_key

    def get_sent_events_key(self):
        return self.sent_events_key

    def get_received_events_key(self):
        return self.received_events_key

    def get_delegated_key_rotation_capability(self):
        return self.delegated_key_rotation_capability

    def get_delegated_withdrawal_capability(self):
        return self.delegated_withdrawal_capability

class BurnEvent(Struct):
    _fields = [
        ("amount", AmountView),
        ("preburn_address", str)
    ]

    def get_amount(self):
        if hasattr(self, "amount"):
            return self.amount

    def get_data(self):
        return None

class CancelBurnEvent(Struct):
    _fields = [
        ("amount", AmountView),
        ("preburn_address", str)
    ]

    def get_amount(self):
        if hasattr(self, "amount"):
            return self.amount

    def get_data(self):
        return None

class MintEvent(Struct):
    _fields = [
        ("amount", AmountView),
    ]

    def get_amount(self):
        if hasattr(self, "amount"):
            return self.amount

    def get_data(self):
        return None

class ToLBRExchangeRateUpdateEvent(Struct):
    _fields = [
        ("currency_code", str),
        ("new_to_lbr_exchange_rate", float),
    ]

    def get_amount(self):
        if hasattr(self, "amount"):
            return self.amount

    def get_data(self):
        return None

class PreburnEvent(Struct):
    _fields = [
        ("amount", AmountView),
        ("preburn_address", str)
    ]

    def get_amount(self):
        if hasattr(self, "amount"):
            return self.amount

    def get_data(self):
        return None

class UpgradeEvent(Struct):
    _fields = [
        ("write_set", str)
    ]

    def get_amount(self):
        if hasattr(self, "amount"):
            return self.amount

    def get_data(self):
        return None

class NewEpochEvent(Struct):
    _fields = [
        ("epoch", Uint64),
    ]

    def get_amount(self):
        if hasattr(self, "amount"):
            return self.amount

    def get_data(self):
        return None

class NewBlockEvent(Struct):
    _fields = [
        ("round", Uint64),
        ("proposer", str),
        ("proposed_time", Uint64),
    ]

    def get_amount(self):
        if hasattr(self, "amount"):
            return self.amount

    def get_data(self):
        return None

class ReceivedPaymentEvent(Struct):
    _fields = [
        ("amount", AmountView),
        ("sender", StrT),
        ("metadata", StrT),
    ]

    def get_amount(self):
        if hasattr(self, "amount"):
            return self.amount

    def get_sender(self):
        return self.sender

    def get_data(self):
        return self.metadata

class SentPaymentEvent(Struct):
    _fields = [
        ("amount", AmountView),
        ("receiver", StrT),
        ("metadata", StrT),
    ]

    def get_amount(self):
        if hasattr(self, "amount"):
            return self.amount

    def get_receiver(self):
        return self.receiver

    def get_data(self):
        return self.metadata

class UnknownEvent(Struct):
    _fields = [
        ("raw", StrT),
    ]

    def get_amount(self):
        if hasattr(self, "amount"):
            return self.amount

    def get_receiver(self):
        return None

    def get_data(self):
        return None

class EventDataView(RustEnum):
    _enums = [
        ("Burn", BurnEvent),
        ("CancelBurn", CancelBurnEvent),
        ("Mint", MintEvent),
        ("ToLBRExchangeRateUpdate", ToLBRExchangeRateUpdateEvent),
        ("Preburn", PreburnEvent),
        ("ReceivedPayment", ReceivedPaymentEvent),
        ("SentPayment", SentPaymentEvent),
        ("Upgrade", UpgradeEvent),
        ("NewEpoch", NewEpochEvent),
        ("NewBlock", NewBlockEvent),
        ("Unknown", UnknownEvent)
    ]

    @classmethod
    def from_value(cls, value):
        if value["type"] == "burn":
            return cls("Burn", BurnEvent.from_value(value))
        if value["type"] == "cancelburn":
            return cls("CancelBurn", CancelBurnEvent.from_value(value))
        if value["type"] == "mint":
            return cls("Mint", MintEvent.from_value(value))
        if value["type"] == "preburn":
            return cls("Preburn", PreburnEvent.from_value(value))
        if value["type"] == "receivedpayment":
            return cls("ReceivedPayment", ReceivedPaymentEvent.from_value(value))
        if value["type"] == "sentpayment":
            return cls("SentPayment", SentPaymentEvent.from_value(value))
        if value["type"] == "upgrade":
            return cls("Upgrade", UpgradeEvent.from_value(value))
        if value["type"] == "newepoch":
            return cls("NewEpoch", NewEpochEvent.from_value(value))
        if value["type"] == "newblock":
            return cls("NewBlock", NewBlockEvent.from_value(value))
        if value["type"] == "unknown":
            return cls("Unknown", UnknownEvent.from_value(value))

    def get_amount(self):
        if self.enum_name != "Unknown":
            return self.value.get_amount()

    def get_data(self):
        if self.enum_name != "Unknown":
            return self.value.get_data()


class EventView(Struct):
    _fields = [
        ("key", StrT),
        ("sequence_number", Uint64),
        ("transaction_version", Uint64),
        ("data", EventDataView),
    ]

    def get_key(self):
        return self.key

    def get_sequence_number(self):
        return self.sequence_number

    def get_transaction_version(self):
        return self.transaction_version

    def get_data(self):
        return self.data.get_data()

    @classmethod
    def vec_from_response(cls, response):
        #TODO
        return response.value

    def get_address(self):
        from move_core_types.account_address import AccountAddress
        key = self.get_key()
        return key[len(key) - AccountAddress.HEX_LENGTH:]

    def get_amount(self):
        return self.data.get_amount()


class PeerToPeerScript(Struct):
    _fields = [
        ("receiver", StrT),
        ("amount", Uint64),
        ("currency", StrT),
        ("metadata", StrT),
        ("metadata_signature", StrT)
    ]

    def get_receiver(self):
        return self.receiver

    def get_amount(self):
        return self.amount

    def get_currency_code(self):
        return self.currency

    def get_data(self):
        return self.metadata

class MintScript(Struct):
    _fields = [
        ("receiver", StrT),
        ("auth_key_prefix", StrT),
        ("amount", Uint64),
        ("currency", StrT),
    ]

    def get_receiver(self):
        return self.receiver

    def get_auth_key_prefix(self):
        return self.auth_key_prefix

    def get_amount(self):
        return self.amount

    def get_currency_code(self):
        return self.currency

class UnknownScript(Struct):
    _fields = [
    ]

class ScriptView(RustEnum):
    _enums = [
        ("PeerToPeer", PeerToPeerScript),
        ("Mint", MintScript),
        ("Unknown", UnknownScript)
    ]

    @classmethod
    def from_value(cls, value):
        type = value.get("type")
        if type == "mint_transaction":
            return cls("Mint", MintScript.from_value(value))
        if type == "peer_to_peer_transaction":
            return cls("PeerToPeer", PeerToPeerScript.from_value(value))
        if type == "unknown_transaction":
            return cls("Unknown", UnknownScript())

    def get_receiver(self):
        if self.enum_name != "Unknown":
            return self.value.get_receiver()

    def get_amount(self):
        if self.enum_name != "Unknown":
            return self.value.get_amount()

    def get_currency_code(self):
        if self.enum_name != "Unknown":
            return self.value.get_currency_code()

    def get_data(self):
        if self.enum_name == "PeerToPeer":
            return self.value.get_data()


class UserTransaction(Struct):
    _fields = [
        ("sender", StrT),
        ("signature_scheme", StrT),
        ("signature", StrT),
        ("public_key", StrT),
        ("sequence_number", Uint64),
        ("max_gas_amount", Uint64),
        ("gas_unit_price", Uint64),
        ("gas_currency", str),
        ("expiration_time", Uint64),
        ("script_hash", StrT),
        ("script", ScriptView)
    ]

    def get_gas_currency(self):
        return self.gas_currency

    def get_sender(self):
        return self.sender

    def get_signature_scheme(self):
        return self.signature_scheme

    def get_signature(self):
        return self.signature

    def get_public_key(self):
        return self.public_key

    def get_sequence_number(self):
        return self.sequence_number

    def get_max_gas_amount(self):
        return self.max_gas_amount

    def get_gas_unit_price(self):
        return self.gas_unit_price

    def get_expiration_time(self):
        return self.expiration_time

    def get_script_hash(self):
        return self.script_hash

    def get_script(self):
        return self.script

    def get_receiver(self):
        return self.script.get_receiver()

    def get_amount(self):
        return self.script.get_amount()

    def get_currency_code(self):
        return self.script.get_currency_code()

    def get_data(self):
        return self.script.get_data()

    def get_code_type(self):
        return get_code_type(self.get_script_hash())


class BlockMetadataView(Struct):
    _fields = [
        ("version", Uint64),
        ("timestamp", Uint64)
    ]

    @classmethod
    def from_response(cls, response):
        return response.value

    def get_version(self):
        return self.version

    def get_timestamp(self):
        return self.timestamp // 10**6

class BlockMetadata(Struct):
    _fields = [
        ("timestamp_usecs", Uint64)
    ]

    def get_timestamp_usecs(self):
        return self.timestamp_usecs // 10**6

class TransactionDataView(RustEnum):
    _enums = [
        ("BlockMetadata", BlockMetadata),
        ("WriteSet", None),
        ("UserTransaction", UserTransaction),
        ("UnknownTransaction", None)
    ]

    @classmethod
    def from_value(cls, value):
        if value.get("type") == "user":
            return cls("UserTransaction", UserTransaction.from_value(value))
        if value.get("type") == "blockmetadata":
            return cls("BlockMetadata", BlockMetadata.from_value(value))
        if value.get("type") == "writeset":
            return cls("WriteSet", None)

    def get_gas_currency(self):
        if self.enum_name == "UserTransaction":
            return self.value.get_gas_currency()

    def get_sender(self):
        if self.enum_name == "UserTransaction":
            return self.value.get_sender()

    def get_receiver(self):
        if self.enum_name == "UserTransaction":
            return self.value.get_receiver()

    def get_amount(self):
        if self.enum_name == "UserTransaction":
            return self.value.get_amount()

    def get_currency_code(self):
        if self.enum_name == "UserTransaction":
            return self.value.get_currency_code()

    def get_data(self):
        if self.enum_name == "UserTransaction":
            return self.value.get_data()

    def get_sequence_number(self):
        if self.enum_name == "UserTransaction":
            return self.value.get_sequence_number()

    def get_expiration_time(self):
        if self.enum_name == "UserTransaction":
            return self.value.get_expiration_time()
        if self.enum_name == "BlockMetadata":
            return self.value.get_timestamp_usecs()

    def get_code_type(self):
        if self.enum_name == "UserTransaction":
            return self.value.get_code_type()
        if self.enum_name == "BlockMetadata":
            return CodeType.BLOCK_METADATA
        if self.enum_name == "WriteSet":
            return CodeType.CHANGE_SET
        if self.enum_name == "UnknownTransaction":
            return CodeType.UNKNOWN

class TransactionView(Struct):
    _fields = [
        ("version", Uint64),
        ("transaction", TransactionDataView),
        ("hash", str),
        ("events", [EventView]),
        ("vm_status", Uint64),
        ("gas_used", Uint64)
    ]

    def get_hash(self):
        return self.hash

    def is_user_transaction(self):
        return self.transaction.enum_name == "UserTransaction"

    def get_public_key(self):
        if self.is_user_transaction():
            return self.transaction.value.get_public_key()

    def get_signature(self):
        if self.is_user_transaction():
            return self.transaction.value.get_signature()

    def get_signature_scheme(self):
        if self.is_user_transaction():
            return self.transaction.value.get_signature_scheme()

    def get_script_hash(self):
        if self.is_user_transaction():
            return self.transaction.value.get_script_hash()

    @classmethod
    def from_response(cls, response):
        return response.value.value

    @classmethod
    def vec_from_response(cls, response):
        return response.value

    def is_successful(self) -> bool:
        return self.vm_status == 4001

    def get_version(self) -> int:
        return self.version

    def get_transaction_data(self) -> TransactionDataView:
        return self.transaction

    def get_events(self) -> List[EventView]:
        return self.events

    def get_vm_status(self) -> int:
        return self.vm_status

    def get_gas_used(self) -> int:
        return self.gas_used

    def get_gas_unit_price(self) ->int:
        if self.is_user_transaction():
            return self.transaction.value.get_gas_unit_price()
        return 0

    def get_gas_used_price(self):
        return self.get_gas_unit_price()*self.get_gas_used()

    def get_gas_currency(self):
        return self.transaction.get_gas_currency()

    def get_sender(self):
        return self.transaction.get_sender()

    def get_code_type(self):
        return self.transaction.get_code_type()

    def get_receiver(self):
        receiver = self.transaction.get_receiver()
        if receiver is None and self.get_code_type() in (CodeType.MINT, ):
            for event in self.events:
                if event.data.enum_name == "ReceivedPayment":
                    return event.get_address()
        return receiver

    def get_amount(self):
        amount = self.transaction.get_amount()
        if amount is None and self.get_code_type() in (CodeType.MINT, ):
            for event in self.events:
                if event.data.enum_name == "ReceivedPayment":
                    return event.get_amount().amount
        return amount

    def get_currency_code(self):
        currency = self.transaction.get_currency_code()
        if currency is None and self.get_code_type() in (CodeType.MINT, ):
            for event in self.events:
                if event.data.enum_name == "ReceivedPayment":
                    return event.get_amount().currency
        return currency

    def get_data(self):
        return self.transaction.get_data()

    def get_sequence_number(self):
        return self.transaction.get_sequence_number()

    def get_expiration_time(self):
        return self.transaction.get_expiration_time()

    def to_json(self):
        tx = dict()
        tx["sender"] = self.get_sender()
        tx["receiver"] = self.get_receiver()
        tx["amount"] = self.get_amount()
        tx["currency_code"] = self.get_currency_code()
        tx["sequence_number"] = self.get_sequence_number()
        tx["major_status"] = self.get_vm_status()
        tx["version"] = self.get_version()
        tx["success"] = self.is_successful()
        tx["expiration_time"] = self.get_expiration_time()
        tx["data"] = self.get_data()
        tx["code_type"] = self.get_code_type()
        return tx

    def __str__(self):
        import json
        amap = self.to_json_serializable()
        return json.dumps(amap, sort_keys=False, indent=2)

    def __repr__(self):
        return self.__str__()

class StateProofView(Struct):
    _fields = [
        ("epoch_change_proof", StrT),
        ("ledger_consistency_proof", StrT),
        ("ledger_info_with_signatures", StrT),
    ]

    @staticmethod
    def from_response(response):
        return response.value

class AccountStateProofView(Struct):
    _fields = [
        ("ledger_info_to_transaction_info_proof", StrT),
        ("transaction_info", StrT),
        ("transaction_info_to_account_proof", StrT),
    ]



class AccountStateBlobView(Struct):
    _fields = [
        ("blob", bytes)
    ]


class AccountStateWithProofView(Struct):
    _fields = [
        ("version", Uint64),
        ("blob", AccountState),
        ("proof", AccountStateProofView)
    ]

    @classmethod
    def from_value(cls, value):
        ret = cls()
        ret.version = value.get("version")
        blob = value.get("blob")
        if blob:
            blob = AccountStateBlobView.deserialize(bytes.fromhex(blob))
            ret.blob = AccountState.deserialize(blob.blob)
        else:
            ret.blob = None

        ret.proof = AccountStateProofView.from_value(value.get("proof"))
        return ret


    def to_json_serializable(self):
        amap = {}
        amap["version"] = self.version
        amap["blob"] = self.blob.to_json_serializable() if self.blob else None
        amap["proof"] = self.proof.to_json_serializable()
        return amap

    @classmethod
    def from_response(cls, response):
        value = response.value
        if value.blob:
            return value.blob
        # raise LibraError(data=StatusCode.ACCOUNT_NOT_EXIST_ERROR)

