import time
from queue import Queue
from flask import Flask
from scan_thread import ScannerThread
from check_thread import CheckerThread
from monitor_thread import MonitorThread
from liquidate_thread import LiquidateBorrowThread, BackLiquidatorThread, LIQUIDATE_LIMIT
from bank import Bank


app = Flask(__name__)

@app.route('/')
def index():
    values = Bank().to_json()
    accounts = values.get("accounts")
    new_accounts = {}
    for addr, account in accounts.items():
        print(account)
        if account.get("owe_amount") >  LIQUIDATE_LIMIT / 1_000_000:
            new_accounts[addr] = account
    values["accounts"] = new_accounts
    return values


if __name__ == "__main__":
    unhealth_queue = Queue()
    scanner_thread = ScannerThread(unhealth_queue)
    scanner_thread.setDaemon(True)
    scanner_thread.start()
    while True:
        time.sleep(2)
        if scanner_thread.state == ScannerThread.UPDATED:
            break


    liquidator_thread = LiquidateBorrowThread(unhealth_queue)
    liquidator_thread.setDaemon(True)
    liquidator_thread.start()

    back_liquidator_thread = BackLiquidatorThread()
    back_liquidator_thread.setDaemon(True)
    back_liquidator_thread.start()

    monitor_thread = MonitorThread()
    monitor_thread.setDaemon(True)
    monitor_thread.start()

    update_state_thread = CheckerThread(unhealth_queue)
    update_state_thread.setDaemon(True)
    update_state_thread.start()

    app.run(host="0.0.0.0", port=9000, debug=False)