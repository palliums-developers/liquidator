from canoser import Struct, Uint64, RustOptional
from crypto.hash import HashValue, TransactionAccumulatorHasher, EventAccumulatorHasher
from lbrtypes.proof import SparseMerkleLeafNode

class AccumulatorProof(Struct):
    _fields = [
        ("siblings", [HashValue])
    ]

    @classmethod
    def from_proto(cls, proto):
        ret = cls()
        ret.siblings = [sibling for sibling in proto.siblings]
        return ret

class LeafCount(Uint64):
    pass

MAX_ACCUMULATOR_PROOF_DEPTH = 63
MAX_ACCUMULATOR_LEAVES = 1 << MAX_ACCUMULATOR_PROOF_DEPTH

class TransactionAccumulatorProof(AccumulatorProof):
    hasher = TransactionAccumulatorHasher

class EventAccumulatorProof(AccumulatorProof):
    hasher = EventAccumulatorHasher

class SparseMerkleLeafNodeOption(RustOptional):
    _type = SparseMerkleLeafNode

    @classmethod
    def from_proto(cls, proto):
        ret = cls()
        ret.value = SparseMerkleLeafNode(proto[0: HashValue.LENGTH], proto[HashValue.LENGTH:HashValue.LENGTH*2])
        return ret

class SparseMerkleProof(Struct):
    _fields = [
        ("leaf", SparseMerkleLeafNodeOption),
        ("siblings", [HashValue]),
    ]

class AccumulatorConsistencyProof(Struct):
    _fields = [
        ("subtrees", [HashValue])
    ]

class AccumulatorRangeProof(Struct):
    _fields = [
        ("left_siblings", [HashValue]),
        ("right_siblings", [HashValue]),
    ]

class TransactionAccumulatorRangeProof(AccumulatorRangeProof):
    hasher = TransactionAccumulatorHasher

class SparseMerkleRangeProof(Struct):
    _fields = [
        ("right_siblings", [HashValue])
    ]

class TransactionProof(Struct):
    _fields = [
        ("ledger_info_to_transaction_info_proof", TransactionAccumulatorProof),
        ("transaction_info", "lbrtypes.transaction.TransactionInfo")
    ]

class AccountStateProof(Struct):
    _fields = [
        ("ledger_info_to_transaction_info_proof", TransactionAccumulatorProof),
        ("transaction_info", "lbrtypes.transaction.TransactionInfo"),
        ("transaction_info_to_account_proof", SparseMerkleProof),
    ]

class EventProof(Struct):
    _fields = [
        ("ledger_info_to_transaction_info_proof", TransactionAccumulatorProof),
        ("transaction_info", "lbrtypes.transaction.TransactionInfo"),
        ("transaction_info_to_event_proof", EventAccumulatorProof),
    ]

class TransactionListProof(Struct):
    _fields = [
        ("ledger_info_to_transaction_infos_proof", TransactionAccumulatorRangeProof),
        ("transaction_infos", ["lbrtypes.transaction.TransactionInfo"]),
    ]