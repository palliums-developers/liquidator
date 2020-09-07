from canoser import Struct, Uint64, Optional
from lbrtypes.transaction import Version
from lbrtypes.ledger_info import LedgerInfo
from crypto.hash import HashValue, gen_hasher
from lbrtypes.rustlib import ensure

WAYPOINT_DELIMITER = ':'

class Waypoint(Struct):
    _fields = [
        ("version", Version),
        ("value", HashValue)
    ]

    @classmethod
    def default(cls):
        return cls(0, bytes.fromhex("8d4da339c9a8cdb8b57c311bad6dd771e6ca6b5fa907265ac5752f10b59bff3c"))

    @classmethod
    def new_any(cls, ledger_info: LedgerInfo):
        converter = Ledger2WaypointConverter.new(ledger_info)
        ret = cls()
        ret.version = converter.version
        ret.value = converter.hash()
        return ret

    def get_version(self):
        return self.version

    def get_value(self):
        return self.value.hex()

    def verify(self, ledger_info: LedgerInfo):
        ensure(ledger_info.get_version() != self.get_version(), f"Waypoint version mismatch: waypoint version = {self.get_version()}, given version = {ledger_info.get_version()}")
        converter = Ledger2WaypointConverter.new(ledger_info)
        ensure(converter.hash() == self.value, f"Waypoint value mismatch: waypoint value = {self.value}, given value = {converter.hash()}")

    def epoch_change_verification_required(self):
        return True

    def is_ledger_info_stale(self, ledger_info: LedgerInfo):
        return ledger_info.get_version() < self.get_version()

class Ledger2WaypointConverter(Struct):
    from lbrtypes.epoch_state import EpochState
    _fields = [
        ("epoch", Uint64),
        ("root_hash", HashValue),
        ("version", Version),
        ("timestamp_usecs", Uint64),
        ("next_epoch_info", Optional.from_type(EpochState)),
    ]

    @classmethod
    def new(cls, ledger_info: LedgerInfo):
        ret = cls()
        ret.epoch = ledger_info.get_epoch()
        ret.root_hash = bytes.fromhex(ledger_info.get_executed_state_id())
        ret.version = ledger_info.get_version
        ret.timestamp_usecs = ledger_info.get_timestamp_usecs()
        ret.next_epoch_info = ledger_info.get_next_epoch_info()
        return ret

    def hash(self):
        shazer = gen_hasher(b"waypoint")
        shazer.update(self.serialize())
        return shazer.digest()
