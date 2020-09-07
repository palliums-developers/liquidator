from enum import IntEnum

class ServerCode(IntEnum):
    DefaultServerError = -32000
    VmValidationError = -32001
    VmVerificationError = -32002
    VmInvariantViolationError = -32003
    VmDeserializationError = -32004
    VmExecutionError = -32005
    VmUnknownError = -32006
    MempoolInvalidSeqNumber = -32007
    MempoolIsFull = -32008
    MempoolTooManyTransactions = -32009
    MempoolInvalidUpdate = -32010
    MempoolVmError = -32011
    MempoolUnknownError = -32012

    VmStatusError = -33000
    WaitTimeoutError = -33001


class StatusCode(IntEnum):
    FETCH_ERROR_MESSAGE = 10001
    WAIT_TIME_OUT = 10002
    ENSURE_ERROR = 10003

    UnknownAuthor = 20001
    TooLittleVotePower = 2002
    TooManySignatures = 20003
    InvalidSignature = 20004

    SerializationError = 30001
    DeserializationError= 30002
    ValidationError = 30003
    WrongLengthError = 3004
    CanonicalRepresentationError = 30005
    SmallSubgroupError = 30006
    PointNotOnCurveError = 30007
    BitVecError = 30008