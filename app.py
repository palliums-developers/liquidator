import time
from flask import request
from queue import Queue
from flask import Flask
from config import config
from chain_scanner import ScannerThread, get_cur_version
from regular_checker import CheckerThread
from cache.api import liquidator_api

app = Flask(__name__)

@app.route('/')
def index():
    ret = {
        "current_version": get_cur_version(),
        "url": config["url"],
        "info": liquidator_api.get_info()
    }
    return ret

@app.route('/version')
def version():
    ret = {
        "current_version": get_cur_version(),
    }
    return ret

if __name__ == "__main__":
    unhealth_queue = Queue(100)
    scanner_thread = ScannerThread(config["url"], unhealth_queue)
    scanner_thread.setDaemon(True)
    scanner_thread.start()
    # while True:
    #     time.sleep(2)
    #     if scanner_thread.state == ScannerThread.UPDATED:
    #         update_state_thread = CheckerThread()
    #         update_state_thread.setDaemon(True)
    #         update_state_thread.start()
    #         break
    app.run(host="0.0.0.0", port=9000, debug=False)