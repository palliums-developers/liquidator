from canoser import Struct, Uint8
from crypto.ed25519 import Ed25519PrivateKey, Ed25519PublicKey, Ed25519Signature, ED25519_PRIVATE_KEY_LENGTH, ED25519_PUBLIC_KEY_LENGTH, ED25519_SIGNATURE_LENGTH
from bitarray import bitarray
from crypto.hash import HashValue
from error import LibraError, StatusCode

MAX_NUM_OF_KEYS = 32
BITMAP_NUM_OF_BYTES = 4

class MultiEd25519PrivateKey(Struct):
    _fields = [
        ("private_keys", [Ed25519PrivateKey]),
        ("threshold", Uint8)
    ]

    @classmethod
    def from_ed25519_private_key(cls, private_key: Ed25519PrivateKey):
        return cls([private_key], 1)

    def sign_message(self, message: HashValue):
        bitmap = bitarray(BITMAP_NUM_OF_BYTES)
        bitmap.setall(False)
        signatures = list(self.threshold)
        for index, private_key in enumerate(self.private_keys):
            if index >= self.threshold:
                break
            bitmap[index] = True
            signatures.append(Ed25519PrivateKey.sign_message(private_key, message))
        return signatures, bitmap.tobytes()

    def sign(self, message):
        signatures, bitmap = self.sign_message(message)
        return MultiEd25519Signature(signatures, bitmap)

    def __len__(self):
        return self.private_keys.__len__()*ED25519_PRIVATE_KEY_LENGTH + 1

class MultiEd25519PublicKey(Struct):
    _fields = [
        ("public_keys", [Ed25519PublicKey]),
        ("threshold", Uint8)
    ]

    def to_bytes(self):
        ret = b""
        for publick_key in self.public_keys:
            ret += publick_key
        ret += self.threshold.to_bytes(1, "little")

    def get_public_keys(self):
        return [key.hex() for key in self.public_keys]

    def get_threshold(self):
        return self.threshold

    @classmethod
    def from_ed25519_public_key(cls, public_key):
        return cls([public_key], 1)

    @classmethod
    def from_multi_ed25519_private_keys(cls, private_keys: MultiEd25519PrivateKey):
        public_keys = [Ed25519PrivateKey.get_public_key(private_key) for private_key in private_keys.private_keys]
        return MultiEd25519PublicKey(public_keys, private_keys.threshold)

    def __len__(self):
        return len(self.public_keys)*ED25519_PUBLIC_KEY_LENGTH + 1

class MultiEd25519Signature(Struct):
    _fields = [
        ("signatures", [Ed25519Signature]),
        ("bitmap", [Uint8, BITMAP_NUM_OF_BYTES])
    ]

    def __len__(self):
        return len(self.signatures) * ED25519_SIGNATURE_LENGTH + BITMAP_NUM_OF_BYTES

    @classmethod
    def from_ed25519_signature(cls, ed_signature: Ed25519Signature):
        bitmap = bitarray(BITMAP_NUM_OF_BYTES).setall(False)
        bitmap[0] = True
        return MultiEd25519Signature([ed_signature], bitmap)

    def verify(self, message, public_key: MultiEd25519PublicKey):
        bitmap = bitarray.frombytes(self.bitmap)
        last_bit = bitmap_last_set_bit(bitmap)
        if last_bit is None or last_bit > len(public_key.get_public_keys()):
            raise LibraError(data=StatusCode.BitVecError, message="Signature index is out of range")
        if bitmap_count_ones(bitmap) < public_key.threshold:
            raise LibraError(data=StatusCode.BitVecError, message="Not enough signatures to meet the threshold")
        bitmap_index = 0
        for sig in self.signatures:
            while bitmap_get_bit(bitmap_index) == False:
                bitmap_index += 1
            sig.verify(message, public_key.public_keys[bitmap_index])
            bitmap_index += 1

def bitmap_set_bit(input, index):
    input[index] = True

def bitmap_get_bit(input: bitarray, index):
    return input[index]

def bitmap_count_ones(input: bitarray):
    return input.count()

def bitmap_last_set_bit(input: bitarray):
    for index, b in enumerate(input.reverse()):
        if b:
            return MAX_NUM_OF_KEYS-1-index

class Multiaddr(bytes):
    pass

