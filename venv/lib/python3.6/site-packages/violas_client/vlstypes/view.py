from extypes.view import TransactionView as ExchangeTransactionView
from banktypes.view import TransactionView as BankTransactionView
from lbrtypes.bytecode import CodeType as LibraCodeType

class TransactionView(ExchangeTransactionView, BankTransactionView):

    @classmethod
    def new(cls, tx):
        ret = super().new(tx)
        ret.__class__ = cls
        return ret

    def get_code_type(self):
        type = ExchangeTransactionView.get_code_type(self)
        if type == LibraCodeType.UNKNOWN:
            return BankTransactionView.get_code_type(self)
        return type

    def get_amount(self):
        return BankTransactionView.get_amount(self)