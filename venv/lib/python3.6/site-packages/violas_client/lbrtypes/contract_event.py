from canoser import Struct, RustEnum, Uint64
from lbrtypes.event import EventKey
from lbrtypes.proof.definition import EventProof
from move_core_types.language_storage import TypeTag, StructTag
from lbrtypes.account_config import ACCOUNT_MODULE_NAME, SENT_EVENT_NAME, RECEIVED_EVENT_NAME, SentPaymentEvent, ReceivedPaymentEvent

class ContractEventV0(Struct):
    _fields = [
        ("key", EventKey),
        ("sequence_number", Uint64),
        ("type_tag", TypeTag),
        ("event_data", bytes)
    ]

    @classmethod
    def from_proto(cls, proto):
        ret = cls()
        ret.key = proto.key
        ret.sequence_number = proto.sequence_number
        ret.type_tag = TypeTag.deserialize(proto.type_tag)
        ret.event_data = proto.event_data
        if ret.get_module_name() == ACCOUNT_MODULE_NAME:
            if ret.get_event_name() == SENT_EVENT_NAME:
                ret.event = SentPaymentEvent.deserialize(proto.event_data)
            elif ret.get_event_name() == RECEIVED_EVENT_NAME:
                ret.event = ReceivedPaymentEvent.deserialize(proto.event_data)
        return ret

    def get_key(self):
        return self.key

    def get_sequence_number(self):
        return self.sequence_number

    def get_type_tag(self) -> TypeTag:
        return self.type_tag

    def get_event_data(self):
        return self.event_data.hex()

    def get_struct_tag(self) -> StructTag:
        return self.type_tag.value

    def get_module_name(self):
        return self.get_struct_tag().module

    def get_module_address(self):
        return self.get_struct_tag().address.hex()

    def get_event_name(self):
        return self.get_struct_tag().name

    def is_sent_or_received_event(self):
        return hasattr(self, "event") and self.get_event_name() in (SENT_EVENT_NAME, RECEIVED_EVENT_NAME)

    def get_amount(self):
        if self.is_sent_or_received_event():
            return self.event.amount

    def get_receiver(self):
        if self.is_sent_or_received_event():
            return self.event.receiver.hex()

    def get_currency_code(self):
        if self.is_sent_or_received_event():
            return self.event.currency_code

    def get_metadata(self):
        if self.is_sent_or_received_event():
            return self.event.metadata.hex()
        return ""

class ContractEvent(RustEnum):
    _enums = [
        ("V0", ContractEventV0)
    ]

    @classmethod
    def from_proto(cls, proto):
        return ContractEvent("V0", ContractEventV0.from_proto(proto))

    def get_struct_tag(self) -> StructTag:
        return self.value.get_struct_tag()

    def get_module_name(self):
        return self.value.get_module_name()

    def get_module_address(self):
        return self.value.get_module_address()

    def get_event_name(self):
        return self.value.get_event_name()

    def get_amount(self):
        return self.value.get_amount()

    def get_receiver(self):
        return self.value.get_receiver()

    def get_currency_code(self):
        return self.value.get_currency_code()

    def get_metadata(self):
        return self.value.get_metadata()

    def get_event_data(self):
        return self.value.get_event_data()

class EventWithProof(Struct):
    _fields = [
        ("transaction_version", Uint64),
        ("event_index", Uint64),
        ("event", ContractEvent),
        ("proof", EventProof),
    ]