from lbrtypes.waypoint import Waypoint
from lbrtypes.ledger_info import LedgerInfoWithSignatures
from lbrtypes.epoch_change import VerifierType, EpochChangeProof
from canoser import Struct, RustEnum
from lbrtypes.epoch_state import EpochState
from lbrtypes.rustlib import ensure
from lbrtypes.ledger_info import LedgerInfo
from lbrtypes.validator_verifier import ValidatorVerifier

class TrustedState(Struct):
    _fields = [
        ("verified_state", Waypoint),
        ("verifier", VerifierType)
    ]

    @classmethod
    def from_waypoint(cls, waypoint: Waypoint):
        if waypoint is None:
            waypoint = Waypoint.default()
        return cls(waypoint, VerifierType("Waypoint", waypoint))

    @classmethod
    def from_epoch_change_ledger_info(cls, latest_version, epoch_change_li: LedgerInfo):
        ensure(latest_version != epoch_change_li.get_version(), "A client can only enter an epoch on the boundary; only with a version inside that epoch",)
        ensure(latest_version > epoch_change_li.get_version(), "The given version must be inside the epoch")
        validator_set = epoch_change_li.get_next_epoch_info()
        ensure(len(validator_set.payload) != 0, "No ValidatorSet in LedgerInfo; it must not be on an epoch boundary")
        epoch_info = EpochState(epoch_change_li.get_epoch() + 1, ValidatorVerifier.from_validator_set(validator_set))
        verifier = VerifierType("TrustedVerifier", epoch_info)
        return cls(latest_version, verifier)

    def verify_and_ratchet(self, latest_li: LedgerInfoWithSignatures, epoch_change_proof: EpochChangeProof):
        res_version = latest_li.get_ledger_info().version
        ensure(res_version >= self.get_latest_version(),
               "The target latest ledger info is stale and behind our current trusted version")
        if self.verifier.epoch_change_verification_required(latest_li.get_ledger_info().next_block_epoch()):
            epoch_change_li = epoch_change_proof.verify(self.verifier)
            new_epoch_state = epoch_change_li.get_ledger_info().get_new_epoch_state()
            pass

    def get_latest_version(self):
        return self.verifier.get_latest_version()

class Version(Struct):
    _fields = [
        ("new_state", TrustedState)
    ]

class Epoch(Struct):
    _fields = [
        ("new_state", TrustedState),
        ("latest_epoch_change_li", LedgerInfoWithSignatures)
    ]


class TrustedStateChange(RustEnum):
    _enums = [
        ("Version", Version),
        ("Epoch", Epoch),
        ("NoChange", None)
    ]

