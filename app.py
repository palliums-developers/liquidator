import time
from queue import Queue
from flask import Flask
from producer.chain_scanner import ScannerThread
from producer.regular_checker import CheckerThread
from cache.api import liquidator_api
from monitor_thread import MonitorThread
from violas_client import Client
from consumer.liquidate_borrow import LiquidateBorrowThread

app = Flask(__name__)

@app.route('/')
def index():
    ret = {
        "current_version": ScannerThread.VERSION,
        "info": liquidator_api.to_json()
    }
    return ret

@app.route('/version')
def version():
    ret = {
        "current_version": ScannerThread.VERSION,
    }
    return ret


if __name__ == "__main__":
    unhealth_queue = Queue(100)
    scanner_thread = ScannerThread(unhealth_queue)
    scanner_thread.setDaemon(True)
    scanner_thread.start()
    while True:
        time.sleep(2)
        if scanner_thread.state == ScannerThread.UPDATED:
            update_state_thread = CheckerThread(unhealth_queue)
            update_state_thread.setDaemon(True)
            update_state_thread.start()
            liquidator_thread = LiquidateBorrowThread(unhealth_queue)
            liquidator_thread.setDaemon(True)
            liquidator_thread.start()
            break

    monitor_thread = MonitorThread()
    monitor_thread.setDaemon(True)
    monitor_thread.start()

    app.run(host="0.0.0.0", port=9000, debug=False)