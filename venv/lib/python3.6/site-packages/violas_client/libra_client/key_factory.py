import hmac
import hashlib
import subprocess


def has_sha3():
    return 'sha3_256' in hashlib.algorithms_available

def sha3_256_mod():
    if has_sha3():
        return hashlib.sha3_256
    else:
        try:
            import sha3
        except ModuleNotFoundError:
            cmd = "python3 -m pip install --user pysha3"
            print("try to install pysha3 with following command:")
            print(cmd)
            subprocess.run(cmd.split(), check=True)
            import sha3
        return sha3.sha3_256

def new_sha3_256():
    return sha3_256_mod()()


class KeyFactory():
    MNEMONIC_SALT_PREFIX = b"LIBRA WALLET: mnemonic salt prefix$"
    MASTER_KEY_SALT = b"LIBRA WALLET: master key salt$"
    INFO_PREFIX = b"LIBRA WALLET: derived key$"

    @classmethod
    def to_seed(cls, mnemonic, passphrase="LIBRA"):
        mnemonic = mnemonic.encode("utf-8")
        passphrase = cls.MNEMONIC_SALT_PREFIX + passphrase.encode("utf-8")
        if has_sha3():
            stretched = hashlib.pbkdf2_hmac("sha3-256", mnemonic, passphrase, 2048)
        else:
            stretched = hashlib.pbkdf2_hmac("sha512", mnemonic, passphrase, 2048)
        return stretched[:64]

    def __init__(self, master):
        self.master = master

    @classmethod
    def new(cls, seed):
        master = hmac.new(KeyFactory.MASTER_KEY_SALT, seed, digestmod=new_sha3_256).digest()
        return cls(master)

    @staticmethod
    def _hkdf_expand(pseudo_random_key, info=b"", length=32):
        shazer = sha3_256_mod()
        hash_len = shazer().digest_size
        length = int(length)
        if length > 255 * hash_len:
            raise Exception("Cannot expand to more than 255 * %d = %d bytes using the specified hash function" %\
                (hash_len, 255 * hash_len))
        blocks_needed = length // hash_len + (0 if length % hash_len == 0 else 1) # ceil
        okm = b""
        output_block = b""
        for counter in range(blocks_needed):
            output_block = hmac.new(pseudo_random_key, output_block + info + bytearray((counter + 1,)),\
                shazer).digest()
            okm += output_block
        return okm[:length]

    def private_child(self, child_index):
        info = KeyFactory.INFO_PREFIX + child_index.to_bytes(8, "little")
        hkdf_expand = self._hkdf_expand(self.master, info, 32)
        return hkdf_expand

