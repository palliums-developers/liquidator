'''
    扫链服务
'''

from threading import Thread
from violas_client import Client
from cache.api import liquidator_api

start_version = 0

def get_cur_version():
    return start_version

class CrawlerThread(Thread):
    def __init__(self, url):
        super(CrawlerThread, self).__init__()
        self.client = Client.new(url)

    def run(self):
        global start_version
        limit = 1000
        while True:
            try:
                txs = self.client.get_transactions(start_version, limit)
                for tx in txs:
                    liquidator_api.add_tx(tx)

            except Exception as e:
                print(e)
                continue
            start_version += len(txs)
            if liquidator_api.update_state is False and len(txs) < limit:
                liquidator_api.update_state = True









