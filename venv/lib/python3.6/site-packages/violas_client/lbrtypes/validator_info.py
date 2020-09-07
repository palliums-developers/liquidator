from canoser import Struct, Uint64
from move_core_types.account_address import AccountAddress
from lbrtypes.validator_config import ValidatorConfig

class ValidatorInfo(Struct):
    _fields = [
        ("account_address", AccountAddress),
        ("consensus_voting_power", Uint64),
        ("config", ValidatorConfig)
    ]

    def get_account_address(self):
        return self.account_address.hex()

    def get_consensus_voting_power(self):
        return self.consensus_voting_power

    def get_network_identity_public_key(self):
        return self.config.network_identity_public_key.hex()

    def get_config(self):
        return self.config
