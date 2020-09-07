from enum import IntEnum

class ExchangeError(IntEnum):
    PATH_ERROR = 10000
    CURRENCY_NOT_REGISTERED = 10001
    PAIR_ERROR = 10002