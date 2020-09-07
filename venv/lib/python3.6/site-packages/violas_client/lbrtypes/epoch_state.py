from canoser import Struct, Uint64
from lbrtypes.validator_verifier import ValidatorVerifier
from lbrtypes.rustlib import ensure

class EpochState(Struct):
    _fields = [
        ("epoch", Uint64),
        ("verifier", ValidatorVerifier)
    ]

    @classmethod
    def empty(cls):
        return cls(0, ValidatorVerifier.new({}))

    def verify(self, ledger_info):
        ensure(self.epoch == ledger_info.get_ledger_info().get_epoch(),
               f"LedgerInfo has uexpected epoch {ledger_info.get_ledger_info().get_epoch()},expected {self.epoch}")
        ledger_info.verify_signatures(self.verifier)

    def epoch_change_verification_required(self, epoch):
        return self.epoch < epoch

    def is_ledger_info_stale(self, ledger_info):
        return ledger_info.get_epoch() < self.epoch
