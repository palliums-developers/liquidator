from nacl.signing import SigningKey
from enum import Enum

from move_core_types.account_address import AccountAddress
from lbrtypes.account_config import treasury_compliance_account_address, association_address, transaction_fee_address
from lbrtypes.transaction.authenticator import AuthenticationKey


AccountStatus = Enum('AccountStatus', ('Local','Persisted','Unknown'))

class Account:
    def __init__(self, private_key, address=None, auth_key=None, sequence_number=0, status=AccountStatus.Unknown):
        if private_key is not None:
            self._signing_key = SigningKey(private_key)
            self._verify_key = self._signing_key.verify_key
        if auth_key:
            self.auth_key = auth_key
        else:
            if hasattr(self, "_verify_key"):
                self.auth_key = AuthenticationKey.ed25519(self.public_key)
        if address:
            self.address = address
        else:
            if hasattr(self, "auth_key"):
                self.address = self.auth_key.derived_address()
        self.sequence_number = sequence_number
        self.status = status


    def json_print_fields(self):
        return ["address", "private_key", "public_key", "auth_key"]

    @classmethod
    def faucet_account(cls, private_key):
        return cls(private_key, treasury_compliance_account_address())

    @classmethod
    def association_account(cls, private_key):
        return cls(private_key, association_address())

    @classmethod
    def transaction_fee_account(cls, private_key):
        return cls(private_key, transaction_fee_address())

    @classmethod
    def load_faucet_account_file(cls, faucet_account_file):
        with open(faucet_account_file, 'rb') as f:
            data = f.read()
            assert len(data) == 33
            assert 32 == data[0]
            private_key = data[1:33]
            return cls.faucet_account(private_key)

    @classmethod
    def load_associate_account_file(cls, associate_account_file):
        with open(associate_account_file, 'rb') as f:
            data = f.read()
            assert len(data) == 33
            assert 32 == data[0]
            private_key = data[1:33]
            return cls.association_account(private_key)

    @classmethod
    def load_transaction_fee_account_file(cls, associate_account_file):
        with open(associate_account_file, 'rb') as f:
            data = f.read()
            assert len(data) == 33
            assert 32 == data[0]
            private_key = data[1:33]
            return cls.transaction_fee_account(private_key)

    def sign(self, message):
        return self._signing_key.sign(message)

    @property
    def address_hex(self):
        return self.address.hex()

    @property
    def auth_key_prefix(self):
        return self.auth_key[0:AccountAddress.LENGTH]

    @property
    def public_key(self):
        return self._verify_key.encode()

    @property
    def private_key(self):
        return self._signing_key.encode()

    @property
    def public_key_hex(self):
        return self.public_key.hex()

    @property
    def private_key_hex(self):
        return self.private_key.hex()
