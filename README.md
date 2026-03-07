# DevOps Take-Home Challenge

Welcome to the Senior DevOps Engineer take-home challenge. This repository contains intentionally broken infrastructure code across four domains. Your goal is to identify and fix the issues in each area.

## How to Submit

1. Go to the **Actions** tab of this repository and run the **"Start Challenge"** workflow when you are ready to begin
2. Clone this repository to your local machine
3. Fix the issues described in the four tasks below
4. Push your changes and open a pull request against the `main` branch of this repository

**Important:**

- You have a **24-hour submission window** starting from when you trigger the "Start Challenge" workflow. Manage your time accordingly.
- After the deadline, this repository will be **archived** and late submissions will **not** be accepted.
- Pull requests opened **before** starting the challenge will be **rejected**. You must run the "Start Challenge" workflow first.

When you create a pull request, your submission will be automatically graded. Results will be posted directly to your PR.

## Task 1: Fix Terraform Security Issues

**File:** `terraform/main.tf`

The Terraform module defines AWS resources with security and configuration problems:

- The security group allows inbound traffic from `0.0.0.0/0` on all ports (0–65535). Restrict the CIDR block and port range to follow least-privilege principles.
- The `aws_security_group` resource is missing a `vpc_id` attribute. Add it so the security group is associated with a VPC.
- The EKS node group uses `m5.24xlarge` instances, which is excessively large and costly. Choose a more reasonable instance type.

No cloud credentials are needed — the Terraform code is evaluated with static analysis only.

## Task 2: Rewrite the Dockerfile for Production

**File:** `python/Dockerfile`

The Dockerfile has several production anti-patterns:

- It uses `ubuntu:latest` as the base image, which is large and uses a mutable tag. Use a slim or distroless base image with a pinned version.
- The application runs as root. Add a non-root user and run the application under it.
- There is no multi-stage build. Consider restructuring the build to reduce the final image size.

The Dockerfile should still install dependencies from `requirements.txt`, copy `app.py`, and run the application on port 8080.

## Task 3: Implement Kubernetes RBAC

**Files:** `kubernetes/rbac.yaml`, `kubernetes/deployment.yaml`

The RBAC manifest (`kubernetes/rbac.yaml`) is empty. You need to create the following resources from scratch:

- A **ServiceAccount** named `log-monitor` in the `default` namespace
- A **Role** that grants `get`, `list`, and `watch` permissions on `pods` and `pods/log` resources
- A **RoleBinding** that binds the Role to the `log-monitor` ServiceAccount

The Deployment (`kubernetes/deployment.yaml`) is also missing the `serviceAccountName` field in its pod spec. Update it so the pod runs under the `log-monitor` ServiceAccount.

## Task 4: Fix the Python Application

**File:** `python/app.py`

The Python Flask application is meant to run inside a Kubernetes cluster, aggregate pod logs, and report pod health. It has several bugs:

- **Authentication:** The app uses `load_kube_config()`, which looks for a local kubeconfig file. Since this app runs inside a cluster, it should use `load_incluster_config()` for in-cluster authentication.
- **Startup:** The startup function calls `list_node()` instead of listing pods. Fix it to call `list_namespaced_pod()` on the `default` namespace and print `"SUCCESS: Found pods in namespace"` to stdout.
- **`/logs` endpoint:** Currently calls `list_node()` and returns an empty response. Fix it to read logs from pods in the namespace using the Kubernetes API, filter log entries to only include `ERROR` and `WARN` severity levels, and return them as structured JSON.
- **`/health` endpoint:** Currently returns a static `{"status": "ok"}` without checking anything. Fix it to query pod statuses in the namespace, identify any pods in `CrashLoopBackOff` or `Error` state, and return a JSON response that reports each pod's health.
- Add proper error handling around Kubernetes API calls.

The app should continue to serve on port 8080 using Flask.
