from kubernetes import client, config
from flask import Flask, jsonify
import threading

app = Flask(__name__)

def init_kube():
    config.load_kube_config()  # BUG: should be load_incluster_config()
    return client.CoreV1Api()

v1 = None

@app.route('/health')
def health():
    # BUG: doesn't check pod statuses
    return jsonify({"status": "ok"})

@app.route('/logs')
def logs():
    # BUG: calls list_node() instead of reading pod logs
    # Returns empty/broken response
    result = v1.list_node()
    return jsonify({"entries": []})

def startup():
    global v1
    v1 = init_kube()
    result = v1.list_node()  # BUG: should be list_namespaced_pod()
    print(f"Found {len(result.items)} items")

if __name__ == "__main__":
    startup()
    app.run(host="0.0.0.0", port=8080)
