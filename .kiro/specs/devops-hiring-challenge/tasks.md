# Implementation Plan: DevOps Hiring Challenge

## Overview

This plan implements a two-repository architecture for an automated DevOps hiring challenge. The public repo (`devops-take-home-test/`) contains intentionally broken code across four domains. The private repo (`private-devops-grader/`) contains the auto-grader, validation workflow, solution files, and test pods. Tasks are ordered so each step builds on the previous, ending with wiring the cross-repo dispatch and validation workflows together.

## Tasks

- [x] 1. Create the broken Terraform module in the public repo
  - [x] 1.1 Create `devops-take-home-test/terraform/main.tf` with intentional security and cost issues
    - Define `aws` provider with `us-east-1` region
    - Define `aws_security_group.eks_sg` with ingress `0.0.0.0/0` on ports `0-65535`, omit `vpc_id`
    - Define `aws_eks_node_group.workers` with `instance_types = ["m5.24xlarge"]`
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 2. Create the broken Dockerfile and Python app in the public repo
  - [x] 2.1 Create `devops-take-home-test/python/Dockerfile` with production anti-patterns
    - Use `ubuntu:latest` base image, run as root, no multi-stage build
    - COPY `requirements.txt` and `app.py`, install deps via pip, CMD `python3 app.py`
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [x] 2.2 Create `devops-take-home-test/python/requirements.txt`
    - Include `kubernetes==28.1.0` and `flask==3.0.0`
    - _Requirements: 4.4_

  - [x] 2.3 Create `devops-take-home-test/python/app.py` with intentional bugs
    - Use `load_kube_config()` instead of `load_incluster_config()`
    - Call `list_node()` instead of correct pod/log APIs
    - `/logs` endpoint returns empty `{"entries": []}` (no log reading/filtering logic)
    - `/health` endpoint returns `{"status": "ok"}` without checking pod statuses
    - Startup calls `list_node()` and prints item count (no "SUCCESS" message)
    - Flask serves on port 8080
    - _Requirements: 4.1, 4.2, 4.7, 4.8, 4.11_

- [x] 3. Create Kubernetes manifests in the public repo
  - [x] 3.1 Create `devops-take-home-test/kubernetes/deployment.yaml`
    - Deployment named `log-reader-app` in `default` namespace
    - Image `log-reader-app:latest`, `imagePullPolicy: Never`
    - Omit `serviceAccountName` field
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [x] 3.2 Create `devops-take-home-test/kubernetes/rbac.yaml` as an empty file
    - File must exist but contain no content
    - _Requirements: 6.1_

- [x] 4. Create the README with candidate instructions in the public repo
  - [x] 4.1 Create `devops-take-home-test/README.md`
    - Describe all four tasks: fix Terraform security issues, rewrite Dockerfile for production, implement Kubernetes RBAC, fix Python app authentication and endpoints
    - Each task describes what is broken and what the expected fix entails
    - Instruct candidates to fork the repo, make fixes, and open a PR against main
    - Document that submissions are auto-graded when a PR is created
    - Do NOT reveal exact grading checks or mention the private grader repo
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 5. Checkpoint — Verify public repo broken code
  - Ensure all public repo files are created and contain the correct intentional bugs. Ask the user if questions arise.


- [x] 6. Create the solution directory in the private repo
  - [x] 6.1 Create `private-devops-grader/solution/terraform/main.tf` with fixed Terraform
    - Restrict security group ingress to specific CIDR and port range, add `vpc_id`
    - Change instance type to a reasonable size (e.g., `m5.large`)
    - _Requirements: 8.5_

  - [x] 6.2 Create `private-devops-grader/solution/python/Dockerfile` with production best practices
    - Use `python:3.11-slim` or similar slim base, add non-root user, pin version
    - _Requirements: 8.5_

  - [x] 6.3 Create `private-devops-grader/solution/python/app.py` with fixed Flask app
    - Use `load_incluster_config()` for in-cluster auth
    - Startup: call `list_namespaced_pod("default")`, print `"SUCCESS: Found pods in namespace"`
    - `/logs` endpoint: read logs from all pods via `read_namespaced_pod_log()`, filter to ERROR/WARN only, return structured JSON `{"entries": [{"pod": "...", "line": "...", "severity": "ERROR|WARN"}, ...]}`
    - `/health` endpoint: list pods via `list_namespaced_pod()`, check container statuses for `CrashLoopBackOff`/`Error`, return `{"status": "ok"|"degraded", "pods": [{"name": "...", "healthy": true|false, "reason": "..."}]}`
    - Handle `ApiException` and `ConfigException` gracefully, return error JSON with HTTP 500 on failure
    - Flask serves on port 8080
    - _Requirements: 4.3, 4.5, 4.6, 4.9, 4.10, 4.11, 8.5_

  - [x] 6.4 Create `private-devops-grader/solution/python/requirements.txt`
    - Include `kubernetes==28.1.0` and `flask==3.0.0`
    - _Requirements: 8.5_

  - [x] 6.5 Create `private-devops-grader/solution/kubernetes/deployment.yaml` with fixed deployment
    - Add `serviceAccountName: log-monitor` to the pod spec
    - _Requirements: 8.5_

  - [x] 6.6 Create `private-devops-grader/solution/kubernetes/rbac.yaml` with complete RBAC
    - ServiceAccount `log-monitor` in `default` namespace
    - Role granting `get`, `list`, `watch` on `pods` and `pods/log`
    - RoleBinding binding the Role to `log-monitor`
    - _Requirements: 6.2, 6.3, 6.4, 8.5_

- [x] 7. Create grader test pods in the private repo
  - [x] 7.1 Create `private-devops-grader/grader/test-logger-pod.yaml`
    - Pod that emits log lines with ERROR, WARN, and INFO severity entries in a loop
    - _Requirements: 7.12_

  - [x] 7.2 Create `private-devops-grader/grader/crash-pod.yaml`
    - Pod that immediately exits with non-zero code to enter `CrashLoopBackOff`
    - _Requirements: 7.13_

- [x] 8. Checkpoint — Verify private repo solution and test pods
  - Ensure all solution files are correct fixes for the broken code, and test pods are properly defined. Ask the user if questions arise.


- [x] 9. Create the auto-grader workflow in the private repo
  - [x] 9.1 Create `private-devops-grader/.github/workflows/main.yml`
    - Trigger on `repository_dispatch` with type `grade-submission`
    - Receive `pr_repo`, `pr_ref`, `pr_number`, `public_repo` from `client_payload`
    - Step: Checkout candidate code from PR ref using `actions/checkout` with `repository` and `ref` from payload
    - Step: Run tfsec against `terraform/` directory (use `continue-on-error: true`)
    - Step: Build Docker image `docker build -t log-reader-app:latest python/`
    - Step: Create KinD cluster via `kind create cluster`
    - Step: Load image into KinD via `kind load docker-image log-reader-app:latest`
    - Step: Apply K8s manifests via `kubectl apply -f kubernetes/`
    - Step: Wait for rollout `kubectl rollout status deployment/log-reader-app --timeout=120s`
    - Step: Validate ServiceAccount `log-monitor` exists via `kubectl get sa log-monitor -n default`
    - Step: Validate RBAC allow — `kubectl auth can-i get pods/log --as=system:serviceaccount:default:log-monitor`
    - Step: Validate RBAC deny — `kubectl auth can-i delete pods --as=system:serviceaccount:default:log-monitor`
    - Step: Validate pod logs contain `"SUCCESS: Found pods in namespace"`
    - Step: Deploy test-logger pod and crashing pod from `grader/` manifests (or inline kubectl run)
    - Step: Wait for test pods to produce logs and crash-pod to enter CrashLoopBackOff (~30s)
    - Step: Port-forward to `log-reader-app` on port 8080
    - Step: Validate `/logs` endpoint — curl, assert valid JSON, contains ERROR/WARN entries, no INFO entries
    - Step: Validate `/health` endpoint — curl, assert valid JSON, identifies crash-pod as unhealthy
    - Step: Post results to candidate's PR via GitHub API using `CROSS_REPO_TOKEN` secret
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 7.10, 7.11, 7.12, 7.13, 7.14, 7.15, 7.16_

- [x] 10. Create the dispatch workflow in the public repo
  - [x] 10.1 Create `devops-take-home-test/.github/workflows/dispatch.yml`
    - Trigger on `pull_request` events targeting `main` branch (opened, synchronize)
    - Step: Create pending check run or PR comment indicating grading has started
    - Step: Send `repository_dispatch` to private repo with event type `grade-submission`
    - Payload: `pr_repo` (head repo clone URL), `pr_ref` (head SHA), `pr_number`, `public_repo`
    - Use `CROSS_REPO_TOKEN` secret for authentication
    - No grading logic, no solution files, no grading criteria in this workflow
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

- [x] 11. Create the E2E validation workflow in the private repo
  - [x] 11.1 Create `private-devops-grader/.github/workflows/validate.yml` scaffold
    - Trigger on `workflow_dispatch` for manual runs
    - Define two sequential jobs: `validate-solution` and `validate-broken` (sad path uses `needs: validate-solution`)
    - Both jobs run on `ubuntu-latest`
    - Configure `VALIDATE_PAT` secret (PAT with `repo`, `delete_repo`, `workflow` scopes)
    - _Requirements: 8.1, 8.2, 8.13, 8.15_

  - [x] 11.2 Implement fork creation and solution push (happy path)
    - In `validate-solution` job:
    - Use GitHub API (`gh` CLI or `curl`) to create a temporary fork of the Public Challenge Repo
    - Clone the fork into the CI runner
    - Checkout the private repo's `solution/` directory
    - Overlay solution files onto the fork's working tree (`solution/terraform/main.tf` → `terraform/main.tf`, etc.)
    - Commit and push to a unique branch (e.g., `validate-solution-${{ github.run_id }}`)
    - _Requirements: 8.4, 8.5, 8.18_

  - [x] 11.3 Implement PR creation and grader result polling (happy path)
    - Open a PR from the fork's branch against the Public Challenge Repo's `main` branch
    - Implement a polling loop (every 30s, ~10 min timeout) that checks the PR for grader results via GitHub API
    - Check for a check run with a conclusion or a PR comment matching a known pattern (e.g., containing "Grading Results")
    - Assert the PR received a "pass" result; exit non-zero if timeout or fail result
    - _Requirements: 8.6, 8.7, 8.8, 8.14, 8.16_

  - [x] 11.4 Implement cleanup (happy path)
    - In an `always()` step at the end of `validate-solution`:
    - Close the PR via GitHub API
    - Delete the remote branch on the fork
    - Delete the temporary fork via GitHub API (`DELETE /repos/{owner}/{fork}`)
    - Log warnings but don't fail the job if cleanup partially fails
    - _Requirements: 8.9_

  - [x] 11.5 Implement fork creation and trivial push (sad path)
    - In `validate-broken` job (runs after `validate-solution`):
    - Create a temporary fork of the Public Challenge Repo
    - Clone the fork, make a trivial change (e.g., add a comment to README) without applying solution fixes
    - Push to a unique branch (e.g., `validate-broken-${{ github.run_id }}`)
    - _Requirements: 8.10, 8.18_

  - [x] 11.6 Implement PR creation and grader result polling (sad path)
    - Open a PR from the fork's branch against the Public Challenge Repo's `main` branch
    - Implement the same polling loop (~10 min timeout) for grader results
    - Assert the PR received a "fail" result; exit non-zero if timeout or pass result
    - _Requirements: 8.11, 8.14, 8.17_

  - [x] 11.7 Implement cleanup (sad path)
    - In an `always()` step at the end of `validate-broken`:
    - Close the PR, delete the remote branch, delete the temporary fork
    - Same cleanup logic as happy path
    - _Requirements: 8.12_

- [x] 12. Checkpoint — Verify all workflows are wired together
  - Ensure dispatch.yml triggers on PR, sends correct payload to private repo. Ensure main.yml receives dispatch and runs all grading steps. Ensure validate.yml tests both solution and broken paths. Ask the user if questions arise.


- [x] 13. Write property tests for solution correctness
  - [x] 13.1 Write property test for RBAC Role permission completeness
    - **Property 1: RBAC Role permission completeness**
    - Generate random subsets of `{get, list, watch}` × `{pods, pods/log}` and verify the solution Role includes all required verb-resource combinations
    - Create test in `private-devops-grader/tests/test_properties.py` using `hypothesis`
    - **Validates: Requirements 6.3**

  - [x] 13.2 Write property test for log severity filtering
    - **Property 4: Log severity filtering**
    - Generate random sets of log lines with mixed severities (ERROR, WARN, INFO, DEBUG), pass through the filtering function, assert output contains only ERROR/WARN and no INFO/DEBUG entries
    - Add test to `private-devops-grader/tests/test_properties.py`
    - **Validates: Requirements 4.5, 4.9**

  - [x] 13.3 Write property test for pod health detection
    - **Property 5: Pod health detection**
    - Generate random sets of pod status objects with `CrashLoopBackOff`, `Error`, or `Running` states, pass through health check function, assert unhealthy pods reported as unhealthy and healthy pods reported as healthy
    - Add test to `private-devops-grader/tests/test_properties.py`
    - **Validates: Requirements 4.6, 4.10**

- [x] 14. Final checkpoint — Full review
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests 2 and 3 (solution passes / broken code fails) are integration properties validated by the `validate.yml` workflow's full E2E fork-PR-dispatch flow (tasks 11.1–11.7), not separate test files
- Property tests 1, 4, and 5 are unit-level property tests using `hypothesis`
- Public repo files go in `devops-take-home-test/`, private repo files go in `private-devops-grader/`
- The E2E validation workflow requires a PAT with `repo`, `delete_repo`, and `workflow` scopes (stored as `VALIDATE_PAT` secret)
don