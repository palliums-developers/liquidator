from json_rpc.views import TransactionView as LibraTransactionView
from json_rpc.views import UserTransaction as LibraUserTransaction
from extypes.bytecode import get_code_type, CodeType
from lbrtypes.bytecode import CodeType as LibraCodeType
from extypes.exdep_resource import MintEvent, BurnEvent, SwapEvent

WITH_EVENT_TYPES = [CodeType.ADD_LIQUIDITY, CodeType.REMOVE_LIQUIDITY, CodeType.SWAP]

def get_swap_event(code_type, data):
    if isinstance(data, str):
        data = bytes.fromhex(data)
    if code_type == CodeType.SWAP:
        return SwapEvent.deserialize(data)
    if code_type == CodeType.ADD_LIQUIDITY:
        return MintEvent.deserialize(data)
    if code_type == CodeType.REMOVE_LIQUIDITY:
        return BurnEvent.deserialize(data)

class TransactionView(LibraTransactionView):
    @classmethod
    def new(cls, tx):
        ret = tx
        ret.__class__ = TransactionView

        if tx.get_code_type() in WITH_EVENT_TYPES:
            for event in ret.events:
                data = event.get_data()
                if len(data):
                    event = get_swap_event(tx.get_code_type(), data)
                    ret.swap_event = event
                    break
        return ret

    def get_code_type(self):
        type = super().get_code_type()
        if type == LibraCodeType.UNKNOWN:
            return get_code_type(self.get_script_hash())
        return type

    def get_swap_event(self):
        if hasattr(self, "swap_event"):
            return self.swap_event

    def get_receiver(self):
        receiver = super().get_receiver()
        if receiver is None and self.get_code_type() in (CodeType.SWAP, ):
            if len(self.events) > 0:
                return self.events[-1].get_address()
        return receiver

    def __str__(self):
        import json
        amap = self.to_json_serializable()
        swap_event = self.get_swap_event()
        if swap_event:
            amap["swap_event"] = swap_event.to_json_serializable()
        return json.dumps(amap, sort_keys=False, indent=2)





