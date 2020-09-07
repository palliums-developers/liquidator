from mnemonic import Mnemonic
from key_factory import KeyFactory
from lbrtypes.rustlib import ensure
from account import Account
from lbrtypes.transaction import RawTransaction
from lbrtypes.transaction import SignedTransaction
import os

class Wallet():
    DELIMITER = ";"
    def __init__(self, mnemonic: bytes, key_factory: KeyFactory, child_number):
        self.mnemonic = mnemonic
        self.key_factory = key_factory
        self.addr_map = {}
        self.child_number = child_number
        self.accounts = []

    @classmethod
    def new(cls):
        m = Mnemonic("english")
        mnemonic = m.generate(192)
        return cls.new_from_mnemonic(mnemonic)

    @classmethod
    def new_from_mnemonic(cls, mnemonic):
        seed = KeyFactory.to_seed(mnemonic)
        key_factory = KeyFactory(seed)
        return cls(mnemonic, key_factory, 0)

    def write_recovery(self, out_file_path: str):
        with open(out_file_path, 'wt') as f:
            f.write(self.mnemonic)
            f.write(self.DELIMITER)
            f.write(str(self.child_number))

    @staticmethod
    def recover(input_file_path: str):
        if os.path.exists(input_file_path):
            with open(input_file_path) as f:
                data = f.read()
                arr = data.split(Wallet.DELIMITER)
                ensure(len(arr) == 2, "Format Error: Wallet must has child num")
                wallet = Wallet.new_from_mnemonic(arr[0])
                wallet.generate_addresses(int(arr[1]))
                return wallet

    def generate_addresses(self, depth):
        current = self.child_number
        ensure(current <= depth, "Addresses already generated up to the supplied depth")
        while self.child_number != depth:
            self.new_account()


    def new_account(self):
        child = Account(self.key_factory.private_child(self.child_number))
        old_child_number = self.child_number
        self.child_number += 1
        ensure(self.addr_map.get(child.address) is None, f"This address is already in your wallet" )
        self.addr_map[child.address] = old_child_number
        self.accounts.append(child)
        return child

    def sign_txn(self, tx: RawTransaction):
        child = self.addr_map.get(tx.sender)
        ensure(child is not None, "Well, that address is nowhere to be found... This is awkward")
        child_key = self.key_factory.private_child(child)
        return SignedTransaction.gen_from_raw_txn(tx, Account(child_key))

    def get_account_by_address_or_refid(self, address_or_refid):
        if isinstance(address_or_refid, str):
            address_or_refid = bytes.fromhex(address_or_refid)
        if isinstance(address_or_refid, bytes):
            id = self.addr_map.get(address_or_refid)
            return self.accounts[id]
        if isinstance(address_or_refid, int):
            return self.accounts[address_or_refid]

