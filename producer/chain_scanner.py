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
    VERSION = 0

    def __init__(self, queue: Queue, config):
        global liquidator_api
        super(ScannerThread, self).__init__()
        self.client = Client.new(URL)
        self.queue = queue
        self.state = self.UPDATING
        if config.get("version") is not None:
            self.__class__.VERSION = config.get("version")
        self.last_version = self.VERSION


    def run(self):
        limit = 1000
        while True:
            txs = self.client.get_transactions(self.VERSION, limit)
            if len(txs) == 0:
                continue
            while True:
                if txs[-1].get_code_type() == CodeType.BLOCK_METADATA:
                    break
                else:
                    tx = self.client.get_transaction(self.VERSION+len(txs))
                    if tx is not None:
                        txs.append(tx)

            for index, tx in enumerate(txs):
                if tx.get_code_type() != CodeType.BLOCK_METADATA:
                    i = 1
                    while True:
                        if txs[index+i].get_code_type() == CodeType.BLOCK_METADATA:
                            timestamp = txs[index+i].get_expiration_time()
                            break
                        i += 1
                    addrs = liquidator_api.add_tx(tx, timestamp)
                    if self.state == self.UPDATED:
                        for addr in addrs:
                            self.queue.put(addr)
            self.__class__.VERSION += len(txs)
            if self.state == self.UPDATING and len(txs) < limit:
                self.state = self.UPDATED
            if self.VERSION - self.last_version >= 100000:
                liquidator_api.update_config(self.VERSION)
                self.last_version = self.VERSION










