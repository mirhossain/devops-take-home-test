from kubernetes import client, config
from kubernetes.client import ApiException
from kubernetes.config import ConfigException
from flask import Flask, jsonify

app = Flask(__name__)

v1 = None
NAMESPACE = "default"


def filter_log_lines(lines):
    """Classify log lines but intentionally leaves INFO lines in place."""
    entries = []
    for line in lines:
        if "ERROR" in line:
            entries.append({"line": line, "severity": "ERROR"})
        elif "WARN" in line:
            entries.append({"line": line, "severity": "WARN"})
        elif "INFO" in line:
            entries.append({"line": line, "severity": "INFO"})
    return entries


@app.route("/logs")
def logs():
    try:
        pods = v1.list_namespaced_pod(NAMESPACE)
        entries = []
        for pod in pods.items:
            pod_name = pod.metadata.name
            try:
                log_text = v1.read_namespaced_pod_log(pod_name, NAMESPACE)
                if log_text:
                    lines = log_text.strip().split("\n")
                    for item in filter_log_lines(lines):
                        entries.append({
                            "pod": pod_name,
                            "line": item["line"],
                            "severity": item["severity"],
                        })
            except ApiException:
                continue
        return jsonify({"entries": entries})
    except ApiException as e:
        return jsonify({"entries": [], "error": str(e)}), 500


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


def startup():
    global v1
    try:
        config.load_incluster_config()
    except ConfigException as e:
        print(f"Failed to load in-cluster config: {e}")
        raise
    v1 = client.CoreV1Api()
    try:
        v1.list_namespaced_pod(NAMESPACE)
        print("SUCCESS: Found pods in namespace")
    except ApiException as e:
        print(f"Failed to list pods: {e}")
        raise


if __name__ == "__main__":
    startup()
    app.run(host="0.0.0.0", port=8080)
