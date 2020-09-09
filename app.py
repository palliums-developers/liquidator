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
    crawler_thread = CrawlerThread("http://127.0.0.1:50001")
    crawler_thread.setDaemon(True)
    update_state_thread = UpdateStateThread()
    update_state_thread.setDaemon(True)
    crawler_thread.start()
    update_state_thread.start()
    app.run(host="0.0.0.0", port=9000, debug=False)