from canoser import Struct, RustEnum
from lbrtypes.ledger_info import LedgerInfoWithSignatures
from lbrtypes.transaction import TransactionWithProof, TransactionListWithProof
from lbrtypes.account_state_blob import AccountStateWithProof
from lbrtypes.contract_event import EventWithProof
from lbrtypes.epoch_change import EpochChangeProof
from lbrtypes.proof.definition import AccumulatorConsistencyProof
from lbrtypes.trusted_state import TrustedState

class GetAccountTransactionBySequenceNumber(Struct):
    _fields = [
        ("transaction_with_proof", TransactionWithProof),
        ("proof_of_current_sequence_number", AccountStateWithProof)
    ]

class GetAccountState(Struct):
    _fields = [
        ("account_state_with_proof", AccountStateWithProof)
    ]

    @classmethod
    def from_proto(cls, proto):
        ret = cls()
        ret.account_state_with_proof = AccountStateWithProof.from_proto(proto.account_state_with_proof)
        return ret


class GetEventsByEventAccessPath(Struct):
    _fields = [
        ("events_with_proof", [EventWithProof]),
        ("proof_of_latest_event", AccountStateWithProof)
    ]

class GetTransactions(Struct):
    _fields = [
        ("txn_list_with_proof", TransactionListWithProof)
    ]

class ResponseItem(RustEnum):
    _enums = [
        ("get_account_transaction_by_sequence_number_response", GetAccountTransactionBySequenceNumber),
        ("get_account_state_response", GetAccountState),
        ("get_events_by_event_access_path_response", GetEventsByEventAccessPath),
        ("get_transactions_response", GetTransactions)
    ]

    @classmethod
    def from_proto(cls, proto):
        if proto.HasField("get_account_transaction_by_sequence_number_response"):
            return ResponseItem("get_account_transaction_by_sequence_number_response", GetAccountTransactionBySequenceNumber.from_proto(proto.get_account_transaction_by_sequence_number_response))
        if proto.HasField("get_account_state_response"):
            return ResponseItem("get_account_state_response", GetAccountState.from_proto(proto.get_account_state_response))
        if proto.HasField("get_events_by_event_access_path_response"):
            return ResponseItem("get_events_by_event_access_path_response", GetEventsByEventAccessPath.from_proto(proto.get_events_by_event_access_path_response))
        if proto.HasField("get_transactions_response"):
            return ResponseItem("get_transactions_response", GetTransactions.from_proto(proto.get_transactions_response))

class UpdateToLatestLedgerResponse(Struct):
    _fields = [
        ("response_items", [ResponseItem]),
        ("ledger_info_with_sigs", LedgerInfoWithSignatures),
        ("epoch_change_proof", EpochChangeProof),
        ("ledger_consistency_proof", AccumulatorConsistencyProof)
    ]

    @classmethod
    def from_proto(cls, proto):
        ret = cls()
        ret.response_items = [ResponseItem.from_proto(item) for item in proto.response_items]
        ret.ledger_info_with_sigs = LedgerInfoWithSignatures.deserialize(proto.ledger_info_with_sigs.bytes)
        ret.epoch_change_proof = EpochChangeProof.from_proto(proto.epoch_change_proof)
        ret.ledger_consistency_proof = AccumulatorConsistencyProof.from_proto(proto.ledger_consistency_proof)
        return ret

    from lbrtypes.ledger_info import LedgerInfo
    def get_ledger_info(self) -> LedgerInfo:
        return self.ledger_info_with_sigs.get_ledger_info()
    

