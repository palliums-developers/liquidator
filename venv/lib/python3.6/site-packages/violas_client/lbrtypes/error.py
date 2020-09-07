from lbrtypes.vm_error import StatusCode
from enum import IntEnum

class LibraError(Exception):
    def __init__(self, status_code, status=None):
        if status_code is None:
            status_code = StatusCode.UNKNOWN_STATUS
        status_code, status = self.handle_enum_code(status_code, status)
        super().__init__(status_code, status)

    @property
    def code(self):
        '''
        Returns
        -------
        :class:`violas.error.status_code.StatusCode`
            status code of the error
        '''
        code, _ = self.args
        return code

    @property
    def msg(self):
        '''
        Returns
        -------
        str
            message of the error
        '''
        _, msg = self.args
        return msg

    @staticmethod
    def handle_enum_code(code, status):
        if not status:
            if isinstance(code, IntEnum):
                status = code.name
            else:
                try:
                    status = StatusCode(code).name
                except:
                    status = "unknown error"
        return code, status