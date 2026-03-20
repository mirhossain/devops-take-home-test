# DevOps Take-Home Challenge

Welcome to the Senior DevOps Engineer take-home challenge. This repository contains intentionally broken infrastructure code across four domains. Your goal is to identify and fix the issues in each area.

## How to Submit

1. Clone this repository to your local machine
2. Fix the issues described in the four tasks below
3. Push your changes and open a pull request against the `main` branch of this repository

> **⚠️ Important:** Opening a pull request is your final submission. Once you create a PR, your repo will be locked to read-only and grading begins immediately. You will not be able to push additional changes after submitting. Make sure your fixes are complete before opening the PR.

Your 24-hour timer started automatically when you provisioned this repo through the challenge portal. Your completion time will be included in the grading results posted to your PR.

When you create a pull request, your submission will be automatically graded. Results will be posted directly to your PR.

## Task 1: Fix Terraform Security Issues

**File:** `terraform/main.tf`

The Terraform module defines AWS resources to simulate an environment.

There are a few problems with the module relating to security, cost management, and correct functionality. Please optimize the file to solve these issues.

No cloud credentials are needed — the Terraform code is evaluated with static analysis only.

## Task 2: Rewrite the Dockerfile for Production

**File:** `python/Dockerfile`

The Dockerfile has several production anti-patterns that can be improved upon.

Please optimize the Dockerfile to reduce build size, fix any security risks, or make any other improvements you deem necessary.

The Dockerfile should still install dependencies from `requirements.txt`, copy `app.py`, and run the application on port 8080.

## Task 3: Implement Kubernetes RBAC

**Files:** `kubernetes/rbac.yaml`, `kubernetes/deployment.yaml`

The RBAC manifest (`kubernetes/rbac.yaml`) is empty. You need to create the following resources from scratch:

- A **ServiceAccount** named `log-monitor` in the `default` namespace
- A **Role** that grants `get`, `list`, and `watch` permissions on `pods` and allows the account to view the pod's `logs`.
- A **RoleBinding** that associates the Role to the `log-monitor` ServiceAccount

The Deployment (`kubernetes/deployment.yaml`) also needs to reference the new ServiceAccount. Update it so the pod runs under the `log-monitor` ServiceAccount.

## Task 4: Fix the Python Application

**File:** `python/app.py`

The Python Flask application is meant to run inside a Kubernetes cluster, aggregate pod logs, and report pod health. It has several bugs currently present.

Treat this task as a behavior contract, not just a syntax cleanup:

- The app must work from inside Kubernetes, not only with a local kubeconfig.
- On startup, the app should verify that it can access pods in the cluster and log a clear success or failure message.
- `GET /logs` should return JSON with an `entries` array. The response should surface only `ERROR` and `WARN` log lines, and each returned entry should include severity information.
- `GET /health` should return JSON with per-pod health details under a `pods` array and should identify unhealthy pods such as crash-looping containers.
- The app should still serve requests on port `8080`.

The Python portion is graded both by source analysis and by running the app inside Kubernetes. If your Deployment or RBAC wiring prevents the app from listing pods or reading pod logs, the Python runtime checks will also lose credit.
