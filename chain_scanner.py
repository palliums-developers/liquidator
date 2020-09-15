'''
    扫链服务
'''
from queue import Queue
from threading import Thread
from violas_client import Client
from cache.api import liquidator_api

start_version = 957774

def get_cur_version():
    return start_version

class ScannerThread(Thread):
    UPDATING = 0
    UPDATED = 1
    def __init__(self, url, queue: Queue):
        super(ScannerThread, self).__init__()
        self.client = Client.new(url)
        self.queue = queue
        self.state = self.UPDATING

    def run(self):
        global start_version
        limit = 1000
        while True:
            # try:
                txs = self.client.get_transactions(start_version, limit)
                for tx in txs:
                    addrs = liquidator_api.add_tx(tx)
                    if self.state == self.UPDATED:
                        for addr in addrs:
                            self.queue.put(addr)
            # except Exception as e:
            #     print(e)
            #     continue
                start_version += len(txs)
                if self.state == self.UPDATING and len(txs) < limit:
                    self.state = self.UPDATED










