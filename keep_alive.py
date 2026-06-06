import threading
import requests
import time
import os

def ping():
    url = os.environ.get('RENDER_EXTERNAL_URL', '')
    if not url:
        return
    while True:
        try:
            requests.get(f"{url}/health", timeout=10)
        except:
            pass
        time.sleep(840)  # every 14 minutes

def start():
    t = threading.Thread(target=ping, daemon=True)
    t.start()
