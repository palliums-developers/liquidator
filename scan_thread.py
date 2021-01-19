'''
    扫链服务
'''
import time
from queue import Queue
from threading import Thread
from bank import Bank
from violas_client.lbrtypes.bytecode import CodeType
from network import create_violas_client

class ScannerThread(Thread):

    UPDATING = 0
    UPDATED = 1

    def __init__(self, queue: Queue):
        super(ScannerThread, self).__init__()
        self.client = create_violas_client()
        self.queue = queue
        self.state = self.UPDATING
        self.bank = Bank()

    def run(self):
        limit = 1000
        self.bank.update_from_db()
        db_height = self.bank.height

        while True:
            try:
                txs = self.client.get_transactions(self.bank.height, limit)
                if len(txs) == 0:
                    time.sleep(1)
                    continue
                for index, tx in enumerate(txs):
                    if tx.get_code_type() == CodeType.UNKNOWN:
                        continue
                    if tx.get_code_type() != CodeType.BLOCK_METADATA and tx.is_successful():
                        addrs = self.bank.add_tx(tx)
                        if self.state == self.UPDATED:
                            if addrs is not None:
                                for addr in addrs:
                                    self.queue.put(addr)
                self.bank.height += len(txs)
                if self.state == self.UPDATING and len(txs) < limit:
                    self.state = self.UPDATED
                if self.bank.height - db_height >= 1_000_000:
                    # start_time = time.time()
                    self.bank.update_to_db()
                    # end_time = time.time()
                    # print("update_to_db need time: ", end_time-start_time)
                    db_height = self.bank.height
            except Exception as e:
                print("scan_thread", e)
                time.sleep(2)
