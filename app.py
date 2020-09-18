from queue import Queue
from flask import Flask
from conf.config import update_config, read_config
from producer.chain_scanner import ScannerThread, URL
from cache.api import liquidator_api

app = Flask(__name__)

@app.route('/')
def index():
    ret = {
        "current_version": ScannerThread.VERSION,
        "url": URL,
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
    config = read_config()
    unhealth_queue = Queue(100)
    scanner_thread = ScannerThread(unhealth_queue, config)
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