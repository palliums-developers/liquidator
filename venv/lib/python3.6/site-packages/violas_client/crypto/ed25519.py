from canoser import DelegateT, BytesT
from nacl.signing import VerifyKey, SigningKey


ED25519_PRIVATE_KEY_LENGTH = 32
ED25519_PUBLIC_KEY_LENGTH = 32
ED25519_SIGNATURE_LENGTH = 64

class Ed25519PrivateKey(DelegateT):
    delegate_type = BytesT(ED25519_PRIVATE_KEY_LENGTH)

    @classmethod
    def sign_message(cls, private_key, message):
        return SigningKey(private_key).sign(message)

    @classmethod
    def get_public_key(cls, private_key):
        return SigningKey(private_key).verify_key

class Ed25519PublicKey(DelegateT):
    delegate_type = BytesT(ED25519_PUBLIC_KEY_LENGTH)

    @classmethod
    def verify_signature(cls, public_key, hash, signature):
        return VerifyKey(public_key).verify(hash, signature)

    @classmethod
    def batch_verify_signatures(cls, hash, keys_and_signatures):
        for public_key, signature in keys_and_signatures:
            cls.verify_signature(public_key, hash, signature)

class Ed25519Signature(DelegateT):
    delegate_type = BytesT(ED25519_SIGNATURE_LENGTH)

    @classmethod
    def verify(cls, message, signature, public_key):
        return Ed25519PublicKey.verify_signature(public_key, message, signature)