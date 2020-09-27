import time
from queue import Queue
from threading import Thread
from cache.api import liquidator_api

class CheckerThread(Thread):
    def __init__(self, queue: Queue):
        super(CheckerThread, self).__init__()
        self.queue = queue
        self.latest_update_time = 0

    def run(self):
        while True:
            try:
                time.sleep(2)
                cur_time = time.time() // 60
                if cur_time > self.latest_update_time:
                    addrs = liquidator_api.check_borrow_index(cur_time)
                    for addr in addrs:
                        self.queue.put(addr)
                self.latest_update_time = cur_time
            except Exception as e:
                print(e)