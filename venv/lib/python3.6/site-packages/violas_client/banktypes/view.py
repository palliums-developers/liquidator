from json_rpc.views import TransactionView as LibraTransactionView
from banktypes.bytecode import get_code_type, CodeType
from lbrtypes.bytecode import CodeType as LibraCodeType
from banktypes.account_resources import ViolasEvent

WITH_AMOUNT_TYPE = [CodeType.BORROW, CodeType.ENTER_BANK, CodeType.EXIT_BANK, CodeType.LIQUIDATE_BORROW, CodeType.LOCK,
                    CodeType.REDEEM, CodeType.REPAY_BORROW]


class TransactionView(LibraTransactionView):
    @classmethod
    def new(cls, tx):
        ret = tx
        ret.__class__ = TransactionView
        return ret

    def get_code_type(self):
        type = super().get_code_type()
        if type == LibraCodeType.UNKNOWN:
            return get_code_type(self.get_script_hash())
        return type

    def get_bank_event(self):
        code_type = self.get_code_type()
        try:
            if code_type in CodeType:
                for event in self.get_events():
                    if event.data.enum_name == "Unknown":
                        return ViolasEvent.deserialize(bytes.fromhex(event.data.value.raw))
        except:
            pass

    def get_amount(self):
        amount = super().get_amount()
        if amount is not None:
            return amount
        event = self.get_bank_event()
        if event is not None:
            return event.get_amount()

    def get_currency_code(self):
        currency_code = super().get_currency_code()
        if currency_code is not None:
            return currency_code
        event = self.get_bank_event()
        if event is not None:
            return event.get_currency_code()

    def get_data(self):
        data = super().get_data()
        if data is None:
            event = self.get_bank_event()
            if event is not None:
                return event.get_data()







