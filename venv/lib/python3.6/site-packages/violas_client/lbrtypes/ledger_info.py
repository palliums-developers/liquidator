from canoser import Struct, RustEnum
from lbrtypes.block_info import BlockInfo
from move_core_types.account_address import AccountAddress
from crypto.hash import HashValue
from crypto.ed25519 import Ed25519Signature

class LedgerInfo(Struct):
    _fields = [
        ("commit_info", BlockInfo),
        ("consensus_data_hash", HashValue)
    ]

    def get_epoch(self):
        return self.commit_info.epoch

    def get_round(self):
        return self.commit_info.round

    def get_id(self):
        return self.commit_info.id.hex()

    def get_executed_state_id(self):
        return self.commit_info.executed_state_id.hex()

    def get_version(self):
        return self.commit_info.version

    def get_timestamp_usecs(self):
        return self.commit_info.timestamp_usecs

    def get_next_epoch_info(self):
        return self.commit_info.next_epoch_info

    def get_consensus_data_hash(self):
        return self.commit_info.consensus_data_hash.hex()


class LedgerInfoWithV0(Struct):
    _fields = [
        ("ledger_info", LedgerInfo),
        ("signatures", {AccountAddress: Ed25519Signature})
    ]

class LedgerInfoWithSignatures(RustEnum):
    _enums = [
        ("V0", LedgerInfoWithV0)
    ]

    def get_ledger_info(self):
        return self.value.ledger_info



