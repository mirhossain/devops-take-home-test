from kubernetes import client, config
from kubernetes.client import ApiException
from kubernetes.config import ConfigException
from flask import Flask, jsonify

app = Flask(__name__)

v1 = None
NAMESPACE = "default"


def filter_log_lines(lines):
    """Filter log lines to only those containing ERROR or WARN severity.

    Args:
        lines: list of log line strings

    Returns:
        list of dicts with keys: line, severity
    """
    entries = []
    for line in lines:
        if "ERROR" in line:
            entries.append({"line": line, "severity": "ERROR"})
        elif "WARN" in line:
            entries.append({"line": line, "severity": "WARN"})
    return entries


def check_pod_health(pod_statuses):
    """Check pod health from a list of pod status objects.

    Args:
        pod_statuses: list of dicts with keys:
            - name: pod name
            - container_statuses: list of dicts with optional keys:
                - waiting: dict with optional "reason" key
                - terminated: dict with optional "reason" key

    Returns:
        dict with keys:
            - status: "ok" or "degraded"
            - pods: list of dicts with keys: name, healthy, reason
    """
    pods = []
    degraded = False
    for pod in pod_statuses:
        name = pod["name"]
        healthy = True
        reason = ""
        for cs in pod.get("container_statuses", []):
            waiting = cs.get("waiting")
            if waiting and waiting.get("reason") in ("CrashLoopBackOff", "Error"):
                healthy = False
                reason = waiting["reason"]
                break
            terminated = cs.get("terminated")
            if terminated and terminated.get("reason") in ("CrashLoopBackOff", "Error"):
                healthy = False
                reason = terminated["reason"]
                break
        if not healthy:
            degraded = True
        pods.append({"name": name, "healthy": healthy, "reason": reason})
    return {"status": "degraded" if degraded else "ok", "pods": pods}


def _extract_pod_statuses(pods):
    """Convert Kubernetes pod objects to the format expected by check_pod_health."""
    statuses = []
    for pod in pods:
        container_statuses = []
        if pod.status and pod.status.container_statuses:
            for cs in pod.status.container_statuses:
                status_info = {}
                if cs.state:
                    if cs.state.waiting:
                        status_info["waiting"] = {"reason": cs.state.waiting.reason or ""}
                    if cs.state.terminated:
                        status_info["terminated"] = {"reason": cs.state.terminated.reason or ""}
                container_statuses.append(status_info)
        statuses.append({
            "name": pod.metadata.name,
            "container_statuses": container_statuses,
        })
    return statuses


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
    try:
        pods = v1.list_namespaced_pod(NAMESPACE)
        pod_statuses = _extract_pod_statuses(pods.items)
        result = check_pod_health(pod_statuses)
        return jsonify(result)
    except ApiException as e:
        return jsonify({"status": "error", "message": str(e)}), 500


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
