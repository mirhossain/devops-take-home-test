from kubernetes import client, config
from flask import Flask, jsonify
import threading

app = Flask(__name__)

def init_kube():
    config.load_kube_config()
    return client.CoreV1Api()

v1 = None

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/logs')
def logs():
    # Returns empty/broken response
    result = v1.list_node()
    return jsonify({"entries": []})

def startup():
    global v1
    v1 = init_kube()
    result = v1.list_node()
    print(f"Found {len(result.items)} items")

if __name__ == "__main__":
    startup()
    # Setup Flask to serve the application here
