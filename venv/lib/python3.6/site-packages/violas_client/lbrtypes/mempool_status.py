from canoser import Struct
from enum import IntEnum

class MempoolStatusCode(IntEnum):
    # Transaction was accepted by Mempool
    Accepted = 0
    # Sequence number is old etc.
    InvalidSeqNumber = 1
    # Mempool is full (reached max global capacity)
    MempoolIsFull = 2
    # Account reached max capacity per account
    TooManyTransactions = 3
    # Invalid update. Only gas price increase is allowed
    InvalidUpdate = 4
    # transaction didn't pass vm_validation
    VmError = 5
    UnknownStatus = 6

class MempoolStatus(Struct):
    _fields = [
        ("code", MempoolStatusCode),
        ("message", str)
    ]