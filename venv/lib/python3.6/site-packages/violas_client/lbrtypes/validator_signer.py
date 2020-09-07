from canoser import Struct
from lbrtypes.move_core.account_address import AccountAddress
from crypto.ed25519 import Ed25519PrivateKey, Ed25519Signature

class ValidatorSigner(Struct):
    _fields = [
        ("author", AccountAddress),
        ("private_key", Ed25519PrivateKey)
    ]

    def get_author(self):
        return self.author.hex()

    def get_private_key(self):
        return self.private_key.hex()

    def sign_message(self, message) -> Ed25519Signature:
        Ed25519PrivateKey.sign_message(self.private_key, message)

    def get_public_key(self):
        return Ed25519PrivateKey.get_public_key(self.private_key).hex()







