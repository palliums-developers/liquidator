from lbrtypes.error import LibraError
from lbrtypes.vm_error import StatusCode

def ensure(code, msg):
    if not code:
        raise LibraError(StatusCode.ENSURE_ERROR, msg)