'''
    扫链服务
'''
from queue import Queue
from threading import Thread
from violas_client import Client
from cache.api import liquidator_api
from conf.config import URL
from violas_client.lbrtypes.bytecode import CodeType

class ScannerThread(Thread):

    UPDATING = 0
    UPDATED = 1
    VERSION = 1823000

    def __init__(self, queue: Queue, config):
        global liquidator_api
        super(ScannerThread, self).__init__()
        self.client = Client.new(URL)
        self.queue = queue
        self.state = self.UPDATING
        if config.get("version") is not None:
            self.__class__.VERSION = config.get("version")
        self.last_version = self.__class__.VERSION

    def run(self):
        limit = 1000
        tx = self.client.get_account_transaction(self.client.ORACLE_OWNER_ADDRESS, 1)
        liquidator_api.add_tx(tx)
        for seq in range(self.client.get_sequence_number(self.client.BANK_OWNER_ADDRESS)):
            tx = self.client.get_account_transaction(self.client.BANK_OWNER_ADDRESS, seq)
            liquidator_api.add_tx(tx)
        while True:
            try:
                txs = self.client.get_transactions(self.__class__.VERSION, limit)
                if len(txs) == 0:
                    continue
                for index, tx in enumerate(txs):
                    if tx.get_code_type() != CodeType.BLOCK_METADATA:
                        addrs = liquidator_api.add_tx(tx)
                        if self.state == self.UPDATED:
                            for addr in addrs:
                                self.queue.put(addr)
                self.__class__.VERSION += len(txs)
                if self.state == self.UPDATING and len(txs) < limit:
                    self.state = self.UPDATED
                if self.__class__.VERSION - self.last_version >= 100000:
                    liquidator_api.update_config(self.__class__.VERSION)
                    self.last_version = self.__class__.VERSION
            except Exception as e:
                print(e)









