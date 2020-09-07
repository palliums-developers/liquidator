from canoser import Uint64, Struct, RustEnum
from move_core_types.account_address import AccountAddress
from lbrtypes.transaction.change_set import ChangeSet
from lbrtypes.transaction.script import Script
from lbrtypes.transaction.module import Module
from lbrtypes.transaction.authenticator import TransactionAuthenticator
from lbrtypes.contract_event import ContractEvent
from lbrtypes.block_metadata import BlockMetadata
from lbrtypes.proof.definition import TransactionListProof, TransactionProof
from crypto.hash import gen_hasher, HashValue
from lbrtypes.bytecode import TransactionType

class Version(Uint64):
    pass

PRE_GENESIS_VERSION = Uint64.max_value
MAX_TRANSACTION_SIZE_IN_BYTES = 4096

class TransactionPayload(RustEnum):
    _enums = [
        ("WriteSet", ChangeSet),
        ("Script", Script),
        ("Module", Module),
    ]

class RawTransaction(Struct):
    _fields = [
        ("sender", AccountAddress),
        ("sequence_number", Uint64),
        ("payload", TransactionPayload),
        ("max_gas_amount", Uint64),
        ("gas_unit_price", Uint64),
        ("gas_currency_code", str),
        ("expiration_time", Uint64),
    ]

    def get_sender(self):
        return self.sender.hex()

    def get_sequence_number(self):
        return self.sequence_number

    def get_max_gas_amount(self):
        return self.max_gas_amount

    def get_gas_unit_price(self):
        return self.gas_unit_price

    def get_expiration_time(self):
        return self.expiration_time

    def hash(self):
        shazer = gen_hasher(b"RawTransaction")
        shazer.update(self.serialize())
        return shazer.digest()

class SignedTransaction(Struct):
    _fields = [
        ("raw_txn", RawTransaction),
        ("authenticator", TransactionAuthenticator),
    ]

    def hash(self):
        shazer = gen_hasher(b"SignedTransaction")
        shazer.update(self.serialize())
        return shazer.digest()

    def get_sender(self):
        return self.raw_txn.get_sender()

    def get_sequence_number(self):
        return self.raw_txn.get_sequence_number()


class Transaction(RustEnum):
    _enums = [
        ("UserTransaction", SignedTransaction),
        ("WaypointWriteSet", ChangeSet),
        ("BlockMetadata", BlockMetadata),
    ]

    def get_raw_txn(self) -> RawTransaction:
        if self.enum_name == "UserTransaction":
            return self.value.raw_txn

    def get_payload(self):
        raw_tx = self.get_raw_txn()
        return raw_tx.payload

    def get_script(self):
        if self.enum_name == "UserTransaction" and self.get_payload().enum_name == "Script":
            return self.value.raw_txn.payload.value

    def get_module(self):
        if self.enum_name == "UserTransaction" and self.get_payload().enum_name == "Module":
            return self.value.raw_txn.payload.value

    def get_code_type(self):
        from lbrtypes.bytecode import CodeType
        if self.enum_name == "BlockMetadata":
            return CodeType.BLOCK_METADATA
        script = self.get_script()
        if script:
            return script.get_code_type()

    def get_code(self):
        script = self.get_script()
        if script:
            return script.code.hex()
        module = self.get_module()
        if module:
            return module.code.hex()

    def get_ty_args(self):
        script = self.get_script()
        if script:
            return script.ty_args

    def get_args(self):
        script = self.get_script()
        if script:
            return script.args

    def get_sender(self):
        raw_txn = self.get_raw_txn()
        if raw_txn:
            return raw_txn.get_sender()

    def get_sequence_number(self):
        raw_txn = self.get_raw_txn()
        if raw_txn:
            return raw_txn.get_sequence_number()

    def get_max_gas_amount(self):
        raw_txn = self.get_raw_txn()
        if raw_txn:
           return raw_txn.get_max_gas_amount()

    def get_gas_unit_price(self):
        raw_txn = self.get_raw_txn()
        if raw_txn:
            return raw_txn.get_gas_unit_price()

    def get_expiration_time(self):
        raw_txn = self.get_raw_txn()
        if raw_txn:
            return raw_txn.get_expiration_time()

class TransactionWithProof(Struct):
    _fields = [
        ("version", Version),
        ("transaction", Transaction),
        ("events", [ContractEvent]),
        ("proof", TransactionProof),
    ]

    @classmethod
    def from_proto(cls, proto):
        if len(proto.transaction.transaction):
            ret = cls()
            ret.version = proto.version
            ret.transaction = Transaction.deserialize(proto.transaction.transaction)
            ret.events = [ContractEvent.from_proto(event) for event in proto.events.events]
            ret.proof = TransactionProof.from_proto(proto.proof)
            return ret

    def to_transaction_without_proof(self):
        return TransactionWithoutProof(self.transaction, self.events, self.version, self.proof.transaction_info)

class TransactionInfo(Struct):
    _fields = [
        ("transaction_hash", HashValue),
        ("state_root_hash", HashValue),
        ("event_root_hash", HashValue),
        ("gas_used", Uint64),
        ("major_status", Uint64),
    ]

    def get_transaction_hash(self):
        return self.transaction_hash.hex()

    def get_state_root_hash(self):
        return self.state_root_hash.hex()

    def get_event_root_hash(self):
        return self.event_root_hash.hex()

    def get_gas_used(self):
        return self.gas_used

    def get_major_status(self):
        return self.major_status

class TransactionListWithProof(Struct):
    _fields = [
        ("transactions", [Transaction]),
        ("events", [[ContractEvent]]),
        ("first_transaction_version", Version),
        ("proof", TransactionListProof),
    ]

    @classmethod
    def from_proto(cls, proto):
        ret = cls()
        ret.transactions = [Transaction.deserialize(transaction.transaction) for transaction in proto.transactions]
        ret.events = []
        for events_for_version in proto.events_for_versions.events_for_version:
            ret.events.append([ContractEvent.from_proto(event) for event in events_for_version.events])
        ret.first_transaction_version = proto.first_transaction_version.value
        ret.proof = TransactionListProof.from_proto(proto.proof)
        return ret

    def to_transactions_without_proof(self):
        zs = zip(self.transactions, self.events, self.proof.transaction_infos)
        txs = []
        for index, tx in enumerate(zs):
            txs.append(TransactionWithoutProof(tx[0], tx[1], self.first_transaction_version + index, tx[2]))
        return txs


class TransactionWithoutProof(Struct):
    _fields = [
        ("transaction", Transaction),
        ("events", [ContractEvent]),
        ("version", Version),
        ("transaction_info", TransactionInfo),
    ]

    def get_module_name(self):
        if len(self.events):
            return self.events[0].get_moudle_name()

    def get_module_address(self):
        if len(self.events):
            return self.events[0].get_module_address()

    def get_args(self):
        return self.transaction.get_args()

    def get_code(self):
        return self.get_transaction().get_code()

    def get_payload(self):
        return self.get_transaction().get_payload()

    def get_transaction(self) -> Transaction:
        return self.transaction

    def get_events(self) -> [ContractEvent]:
        return self.events

    def get_version(self):
        return self.version

    def get_transaction_info(self) -> TransactionInfo:
        return self.transaction_info

    def get_transaction_type(self):
        if isinstance(self.transaction.value, SignedTransaction):
            return TransactionType.SIGNED_TRANSACTION
        if isinstance(self.transaction.value, BlockMetadata):
            return TransactionType.BLOCK_METADATA
        if isinstance(self.transaction.value, ChangeSet):
            return TransactionType.CHANGE_SET

    def get_code_type(self):
        return self.transaction.get_code_type()

    def get_receiver(self):
        if len(self.events):
            return self.events[0].get_receiver()

    def get_amount(self):
        if len(self.events):
            return self.events[0].get_amount()

    def get_data(self):
        if len(self.events):
            return self.events[0].get_metadata()
        return ""

    def is_executed(self):
        return self.get_major_status() == 4001

    def get_transaction_hash(self):
        return self.transaction_info.get_transaction_hash()

    def get_state_root_hash(self):
        return self.transaction_info.get_state_root_hash()

    def get_event_root_hash(self):
        return self.transaction_info.get_event_root_hash()

    def get_gas_used(self):
        return self.transaction_info.gas_used

    def get_major_status(self):
        return self.transaction_info.major_status

    def get_sender(self):
        return self.transaction.get_sender()

    def get_sequence_number(self):
        return self.transaction.get_sequence_number()

    def get_max_gas_amount(self):
        return self.transaction.get_max_gas_amount()

    def get_gas_unit_price(self):
        return self.transaction.get_gas_unit_price()

    def get_expiration_time(self):
        return self.transaction.get_expiration_time()

    def get_id(self):
        if self.get_transaction_type() == TransactionType.BLOCK_METADATA:
            return self.get_transaction().value.get_id()

    def get_round(self):
        if self.get_transaction_type() == TransactionType.BLOCK_METADATA:
            return self.get_transaction().value.get_round()

    def get_timestamp_usecs(self):
        if self.get_transaction_type() == TransactionType.BLOCK_METADATA:
            return self.get_transaction().value.get_timestamp_usecs()

    def get_previous_block_votes(self):
        if self.get_transaction_type() == TransactionType.BLOCK_METADATA:
            return self.get_transaction().value.get_previous_block_votes()

    def get_proposer(self):
        if self.get_transaction_type() == TransactionType.BLOCK_METADATA:
            return self.get_transaction().value.get_proposer()
