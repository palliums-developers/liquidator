import time
from queue import Queue
from threading import Thread
from bank import Bank

class CheckerThread(Thread):
    def __init__(self, queue: Queue):
        super(CheckerThread, self).__init__()
        self.queue = queue
        self.latest_update_time = 0
        self.bank = Bank()

    def run(self):
        while True:
            try:
                cur_time = int(time.time() // 60)
                print(cur_time, self.latest_update_time)
                if cur_time > self.latest_update_time:
                    addrs = self.bank.check_borrow_index(cur_time)
                    print("len quene", self.queue.qsize(), len(addrs))
                    for addr in addrs:
                        print(addrs)
                        self.queue.put(addr)
                    print("end")
                self.latest_update_time = cur_time
                time.sleep(60)
            except Exception as e:
                import traceback
                time.sleep(2)
                print("check_thread", traceback.print_exc())
