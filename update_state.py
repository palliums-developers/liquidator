import time
from threading import Thread
from cache.api import liquidator_api

class UpdateStateThread(Thread):
    def __init__(self, intervals=5):
        super(UpdateStateThread, self).__init__()
        self.intervals = intervals

    def run(self):
        while True:
            time.sleep(self.intervals)
            liquidator_api.update_accounts_liquidation_state()
