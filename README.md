# DevOps Take-Home Challenge

Welcome to the Senior DevOps Engineer take-home challenge. This repository contains intentionally broken infrastructure code across four domains. Your goal is to identify and fix the issues in each area.

## How to Submit

1. Clone this repository to your local machine
2. Fix the issues described in the four tasks below
3. Push your changes and open a pull request against the `main` branch of this repository

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

Please optimize the usage of the Kubernetes SDK to fix any functional issues as well as optimize the program itself with improved error handling, logging, etc.

Additionally, The app should serve requests on port 8080 using Flask.
