from enum import IntEnum
from error.status_code import ServerCode
from lbrtypes.vm_error import StatusCode as LibraStatusCode

class LibraError(Exception):
    def __init__(self, server_code=None, data=None, message=None):
        server_code = LibraError.parse_server_code(server_code)
        data = LibraError.parse_data(data)
        message = LibraError.parse_message(message)
        super().__init__(server_code, data, message)

    @staticmethod
    def parse_server_code(server_code):
        if isinstance(server_code, IntEnum):
            return server_code
        if isinstance(server_code, int):
            try:
                return ServerCode(server_code)
            except:
                pass
        return server_code

    @classmethod
    def parse_data(cls, data):
        if isinstance(data, IntEnum):
            return {'major_status': data, 'message': data.name, 'sub_status': None}
        if isinstance(data, int):
            try:
                data = LibraStatusCode(data)
                return {'major_status': data, 'message': data.name, 'sub_status': None}
            except:
                return {'major_status': data, 'message': None, 'sub_status': None}
        return data

    @classmethod
    def parse_message(cls, message):
        return message

    @classmethod
    def from_response(cls, resp):
        code = resp.get("code")
        data = resp.get("data")
        message = resp.get("message")
        return cls(code, data, message)

    @property
    def code(self):
        '''
        Returns
        -------
        :class:`violas.error.status_code.StatusCode`
            status code of the error
        '''
        code, _, _ = self.args
        return code

    @property
    def data(self):
        '''
        Returns
        -------
        str
            message of the error
        '''
        _, data, _ = self.args
        return data


    @property
    def msg(self):
        '''
        Returns
        -------
        str
            message of the error
        '''
        _, _, msg = self.args
        return msg

    @staticmethod
    def handle_enum_code(code, message):
        if not message:
            message = LibraStatusCode.get_name(code)
        return code, message

