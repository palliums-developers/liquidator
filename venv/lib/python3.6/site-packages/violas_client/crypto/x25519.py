from canoser import DelegateT, BytesT

# Size of a X25519 private key
PRIVATE_KEY_SIZE = 32

# Size of a X25519 public key
PUBLIC_KEY_SIZE = 32

# Size of a X25519 shared secret
SHARED_SECRET_SIZE = 32

class PrivateKey(DelegateT):
    delegate_type = BytesT(PRIVATE_KEY_SIZE)

class PublicKey(DelegateT):
    delegate_type = BytesT(PUBLIC_KEY_SIZE)