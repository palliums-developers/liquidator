from flask import Flask
from cache.api import liquidator_api
from crawler import CrawlerThread
from update_state import UpdateStateThread
from crawler import get_cur_version
app = Flask(__name__)

@app.route('/')
def index():
    ret = {
        "current_version": get_cur_version(),
        "state": liquidator_api.accounts_view.to_json(),
    }
    return ret

if __name__ == "__main__":
    crawler_thread = CrawlerThread("bj_testnet")
    crawler_thread.setDaemon(True)
    update_state_thread = UpdateStateThread()
    update_state_thread.setDaemon(True)
    crawler_thread.start()
    update_state_thread.start()
    app.run(host="localhost", port=8000, debug=False)