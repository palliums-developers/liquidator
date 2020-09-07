from canoser import Struct, Uint64
from move_core_types.account_address import AccountAddress as Address
from crypto.ed25519 import Ed25519PublicKey, Ed25519Signature
from lbrtypes.rustlib import ensure
from error import LibraError, StatusCode

class ValidatorConsensusInfo(Struct):
    _fields = [
        ("public_key", Ed25519PublicKey),
        ("voting_power", Uint64)
    ]

    def get_public_key(self):
        return self.public_key.hex()

    def get_voting_power(self):
        return self.voting_power


class ValidatorVerifier(Struct):
    _fields = [
        ('address_to_validator_info', {Address: ValidatorConsensusInfo}),
        ('quorum_voting_power', Uint64),
        ('total_voting_power', Uint64)
    ]

    @classmethod
    def new(cls, address_to_validator_info):
        ret = cls()
        ret.address_to_validator_info = address_to_validator_info
        ret.total_voting_power = sum(address_to_validator_info.values())
        if len(address_to_validator_info) == 0:
            ret.quorum_voting_power = 0
        else:
            ret.quorum_voting_power = ret.total_voting_power * 2 // 3 + 1
        return ret

    @classmethod
    def new_with_quorum_voting_power(cls, address_to_validaotr_info, quorum_voting_power):
        total_voting_power = 0
        for voting_power in address_to_validaotr_info.values():
            total_voting_power += voting_power
        ensure(quorum_voting_power <= total_voting_power,
                f"Quorum voting power is greater than the sum of all voting power of authors: {quorum_voting_power}, quorum_size: {quorum_voting_power}.")
        return cls(address_to_validaotr_info, quorum_voting_power, total_voting_power)

    @classmethod
    def new_single(cls, author: Address, public_key: Ed25519PublicKey):
        author_to_validator_info = dict()
        author_to_validator_info[author] = ValidatorConsensusInfo(public_key, 1)
        return cls.new(author_to_validator_info)

    def verify_signature(self, author: Address, hash: bytes, signature: Ed25519Signature):
        public_key = self.get_public_key(author)
        ensure(Ed25519PublicKey.verify_signature(bytes.fromhex(public_key), hash, signature),
               f"signature:{signature.hex()} mismatch public_key: {public_key}")

    def verify_aggregated_signature(self, hash, aggregated_signature: {Address: Ed25519Signature}):
        self.check_num_of_signatures(aggregated_signature)
        self.check_voting_power(aggregated_signature.keys())
        for author, signature in aggregated_signature:
            self.verify_signature(author, hash, signature)

    def batch_verify_aggregated_signature(self, hash, aggregated_signature: {Address: Ed25519Signature}):
        self.check_num_of_signatures(aggregated_signature)
        self.check_voting_power(aggregated_signature.keys())
        keys_and_signatures = {bytes.fromhex(self.get_public_key(address)): signature for address, signature in aggregated_signature}
        if Ed25519PublicKey.batch_verify_signatures(hash, keys_and_signatures):
            self.verify_aggregated_signature(hash, aggregated_signature)

    def check_num_of_signatures(
        self,
        aggregated_signature: {Address: Ed25519Signature},
    ):
        num_of_signatures = len(aggregated_signature)
        if num_of_signatures > len(self):
            raise LibraError(data = StatusCode.TOO_MANY_SIGNATURES)

    def check_voting_power(self, authors):
        aggregated_voting_power = 0
        for account_address in authors:
            voting_power = self.get_voting_power(account_address)
            aggregated_voting_power += voting_power

        if aggregated_voting_power < self.quorum_voting_power:
            raise LibraError(data=StatusCode.TOO_LITTLE_VOTE_POWER)

    def get_public_key(self, author: Address):
        validator_info = self.address_to_validator_info.get(author)
        if validator_info:
            return validator_info.get_public_key()
        raise LibraError(data=StatusCode.UnknownAuthor, message=f"Address:{author} is not a validator")

    def get_voting_power(self, author: Address):
        validator_info = self.address_to_validator_info.get(author)
        if validator_info:
            return validator_info.get_voting_power()
        raise LibraError(data=StatusCode.UnknownAuthor, message=f"Address:{author} is not a validator")

    def __len__(self):
        return self.address_to_validator.__len__()

    def is_empty(self):
        return len(self) == 0

    def quorum_voting_power(self):
        return self.quorum_voting_power