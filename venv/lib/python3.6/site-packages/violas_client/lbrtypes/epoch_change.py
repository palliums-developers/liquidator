from canoser import Struct, RustEnum
from lbrtypes.waypoint import Waypoint
from lbrtypes.epoch_state import EpochState
from lbrtypes.ledger_info import LedgerInfoWithSignatures
from lbrtypes.rustlib import ensure

class EpochChangeProof(Struct):
    _fields = [
        ("ledger_info_with_sigs", [LedgerInfoWithSignatures]),
        ("more", bool)
    ]

    @classmethod
    def from_proto(cls, proto):
        ret = cls()
        ret.ledger_info_with_sigs = [LedgerInfoWithSignatures.deserialize(signature.bytes) for signature in proto.ledger_info_with_sigs]
        ret.more = proto.more
        return ret

    def get_epoch(self):
        ledger_info_with_sigs = self.ledger_info_with_sigs
        if len(ledger_info_with_sigs):
            return self.ledger_info_with_sigs[0].get_ledger_info().get_epoch()

    def verify(self, verifier):
        ensure(len(self.ledger_info_with_sigs), "The EpochChangeProof is empty")
        ensure(verifier.is_ledger_info_stale(self.ledger_info_with_sigs[-1].get_ledger_info()),
               "The EpochChangeProof is stale as our verifier is already ahead \
             of the entire EpochChangeProof")
        for ledger_info_with_sigs in self.ledger_info_with_sigs:
            if verifier.is_ledger_info_stale(ledger_info_with_sigs.get_ledger_info()):
                verifier.verify(ledger_info_with_sigs)
            verifier_ref = ledger_info_with_sigs.get_ledger_info().get_next_epoch_state()
        return self.ledger_info_with_sigs[-1]


class VerifierType(RustEnum):
    _enums = [
        ("Waypoint", Waypoint),
        ("TrustedVerifier", EpochState)
    ]

    def get_latest_version(self):
        if self.enum_name == "Waypoint":
            return self.value.version
        return 0
