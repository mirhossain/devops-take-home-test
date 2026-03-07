# Requirements Document

## Introduction

This feature is a two-repository architecture used as an automated technical screening challenge for Senior DevOps Engineer candidates. A public challenge repository contains intentionally broken and insecure infrastructure code across Terraform, Docker, Kubernetes, and Python domains. Candidates fork the public repo, fix the issues, and create a pull request against it. A lightweight dispatch workflow in the public repo triggers the actual grading pipeline in a separate private repository. The private grader repo contains all grading logic, the solution directory, and the end-to-end validation workflow — none of which are visible to candidates. This architecture prevents candidates from reverse-engineering the grading criteria.

## Glossary

- **Public_Challenge_Repo**: The public GitHub repository that candidates fork. Contains the broken code, README with instructions, and a lightweight dispatch workflow that triggers the private grader. No grading logic lives here.
- **Private_Grader_Repo**: A private GitHub repository that contains the auto-grader workflow, the solution/ directory, and all grading logic. Not visible to candidates.
- **Auto_Grader**: A GitHub Actions workflow in the Private_Grader_Repo that automatically evaluates candidate submissions against predefined correctness checks
- **Dispatch_Workflow**: A lightweight GitHub Actions workflow in the Public_Challenge_Repo that triggers the Auto_Grader in the Private_Grader_Repo via `repository_dispatch`
- **KinD_Cluster**: A Kubernetes-in-Docker cluster spun up ephemerally within the CI pipeline for deployment validation
- **Candidate**: A Senior DevOps Engineer applicant completing the challenge
- **Terraform_Module**: The `terraform/main.tf` file containing intentionally insecure AWS infrastructure definitions
- **Dockerfile**: The `python/Dockerfile` containing an intentionally poorly written container build definition
- **Python_App**: The `python/app.py` Flask application that authenticates to the Kubernetes API, aggregates and filters pod logs by severity, reports pod health status via HTTP endpoints, and prints a startup success message
- **RBAC_Manifest**: The `kubernetes/rbac.yaml` file where candidates define Kubernetes Role-Based Access Control resources
- **Deployment_Manifest**: The `kubernetes/deployment.yaml` file defining the Kubernetes Deployment for the Python app
- **tfsec**: A static analysis tool that scans Terraform code for security misconfigurations
- **Log_Reader_App**: The Kubernetes Deployment name (`log-reader-app`) used for the Python application
- **Log_Monitor**: The Kubernetes ServiceAccount name (`log-monitor`) used for RBAC bindings
- **Cross_Repo_PAT**: A GitHub Personal Access Token (or GitHub App token) stored as a secret in both repos, used for cross-repo workflow dispatch and PR status reporting

## Requirements

### Requirement 1: Candidate Instructions

**User Story:** As a candidate, I want clear instructions in the README of the public challenge repo describing all four challenge tasks, so that I understand what needs to be fixed and how my submission will be graded.

#### Acceptance Criteria

1. THE Public_Challenge_Repo SHALL contain a `README.md` file at the repository root describing four tasks: fix Terraform security issues, rewrite Dockerfile for production, implement Kubernetes RBAC, and fix Python app authentication for in-cluster use
2. WHEN a candidate reads the README, THE Public_Challenge_Repo SHALL present each task with a description of what is broken and what the expected fix entails
3. THE Public_Challenge_Repo SHALL document in the README that submissions are auto-graded when a pull request is created against the public repo's main branch
4. THE README SHALL instruct candidates to fork the Public_Challenge_Repo, make their fixes, and open a pull request back against the Public_Challenge_Repo

### Requirement 2: Intentionally Broken Terraform Module

**User Story:** As a hiring manager, I want the Terraform code to contain specific security and cost issues, so that candidates demonstrate their ability to identify and remediate infrastructure misconfigurations.

#### Acceptance Criteria

1. THE Terraform_Module SHALL define an AWS security group with an ingress rule allowing traffic from `0.0.0.0/0` on all ports
2. THE Terraform_Module SHALL define an EKS managed node group using instance type `m5.24xlarge`
3. THE Terraform_Module SHALL omit the `vpc_id` attribute on the `aws_security_group` resource
4. WHEN tfsec scans the Terraform_Module in its initial broken state, THE Auto_Grader SHALL detect one or more security findings

### Requirement 3: Intentionally Bad Dockerfile

**User Story:** As a hiring manager, I want the Dockerfile to contain production anti-patterns, so that candidates demonstrate container security and optimization knowledge.

#### Acceptance Criteria

1. THE Dockerfile SHALL use `ubuntu:latest` as the base image
2. THE Dockerfile SHALL run the application as the root user
3. THE Dockerfile SHALL lack a multi-stage build or slim/distroless base image
4. THE Dockerfile SHALL copy `requirements.txt` and `app.py` and install dependencies via pip
5. THE Dockerfile SHALL define `CMD` to run `python app.py`

### Requirement 4: Intentionally Broken Python Application

**User Story:** As a hiring manager, I want the Python app to contain authentication bugs, broken API calls, and incomplete HTTP endpoint logic, so that candidates demonstrate Kubernetes SDK proficiency, log aggregation skills, and the ability to build observable microservices.

#### Acceptance Criteria

1. THE Python_App SHALL use `load_kube_config()` instead of `load_incluster_config()` for Kubernetes authentication
2. THE Python_App SHALL call `list_node()` instead of the correct Kubernetes API calls for reading pods and pod logs
3. WHEN a candidate fixes the Python_App, THE Python_App SHALL output the string "SUCCESS: Found pods in namespace" to stdout upon successfully listing pods at startup
4. THE Public_Challenge_Repo SHALL contain a `python/requirements.txt` file specifying `kubernetes==28.1.0` and `flask`
5. THE Python_App SHALL expose an HTTP endpoint at `/logs` that returns a JSON response containing log entries filtered to only ERROR and WARN severity levels from pods in the namespace
6. THE Python_App SHALL expose an HTTP endpoint at `/health` that returns a JSON response including the health status of pods in the namespace, identifying any pods in `CrashLoopBackOff` or `Error` state
7. WHEN the broken Python_App is deployed, THE `/logs` endpoint SHALL return an empty response or fail because the log reading and filtering logic is not implemented
8. WHEN the broken Python_App is deployed, THE `/health` endpoint SHALL NOT report pod health statuses because the pod status checking logic is not implemented
9. WHEN a candidate fixes the Python_App, THE `/logs` endpoint SHALL return valid JSON containing only ERROR and WARN log entries and SHALL NOT include INFO-level entries
10. WHEN a candidate fixes the Python_App, THE `/health` endpoint SHALL return valid JSON that correctly identifies pods in `CrashLoopBackOff` or `Error` state as unhealthy
11. THE Python_App SHALL use Flask to serve the HTTP endpoints on a configurable port (default 8080)

### Requirement 5: Kubernetes Deployment Manifest

**User Story:** As a hiring manager, I want the Deployment manifest to be missing the serviceAccountName, so that candidates demonstrate knowledge of Kubernetes pod identity configuration.

#### Acceptance Criteria

1. THE Deployment_Manifest SHALL define a Deployment named `log-reader-app` in the `default` namespace
2. THE Deployment_Manifest SHALL use a container image reference that matches the image built and loaded into the KinD_Cluster
3. THE Deployment_Manifest SHALL omit the `serviceAccountName` field in the pod spec
4. THE Deployment_Manifest SHALL set `imagePullPolicy` to `Never` so the locally loaded image is used in KinD

### Requirement 6: Blank RBAC Manifest

**User Story:** As a hiring manager, I want the RBAC manifest to be blank, so that candidates demonstrate their ability to author Kubernetes RBAC resources from scratch.

#### Acceptance Criteria

1. THE RBAC_Manifest SHALL exist as an empty file at `kubernetes/rbac.yaml`
2. WHEN a candidate completes the RBAC task, THE RBAC_Manifest SHALL define a ServiceAccount named `log-monitor`
3. WHEN a candidate completes the RBAC task, THE RBAC_Manifest SHALL define a Role granting `get`, `list`, and `watch` permissions on `pods` and `pods/log` resources
4. WHEN a candidate completes the RBAC task, THE RBAC_Manifest SHALL define a RoleBinding binding the Role to the `log-monitor` ServiceAccount

### Requirement 7: Auto-Grader Pipeline (Private Repo)

**User Story:** As a hiring manager, I want an automated grading pipeline in a private repository that validates all four challenge areas, so that candidate submissions are evaluated consistently without exposing grading criteria.

#### Acceptance Criteria

1. THE Auto_Grader SHALL be defined in `.github/workflows/main.yml` in the Private_Grader_Repo and trigger on `repository_dispatch` events with type `grade-submission`
2. WHEN the Auto_Grader is triggered, it SHALL receive the candidate's PR repository URL, branch ref, and PR number from the dispatch payload
3. WHEN the pipeline runs, THE Auto_Grader SHALL check out the candidate's code from the Public_Challenge_Repo using the PR ref provided in the dispatch payload
4. WHEN the pipeline runs, THE Auto_Grader SHALL execute tfsec against the `terraform/` directory and report findings
5. WHEN the pipeline runs, THE Auto_Grader SHALL build the Docker image from `python/Dockerfile` with the tag `log-reader-app:latest`
6. WHEN the pipeline runs, THE Auto_Grader SHALL create a KinD_Cluster, load the built image into the cluster, and apply all Kubernetes manifests from the `kubernetes/` directory
7. WHEN the pipeline runs, THE Auto_Grader SHALL wait for the `log-reader-app` Deployment to roll out successfully within a timeout period
8. WHEN the pipeline runs, THE Auto_Grader SHALL validate that a ServiceAccount named `log-monitor` exists in the `default` namespace
9. WHEN the pipeline runs, THE Auto_Grader SHALL validate that the `log-monitor` ServiceAccount can `get` pods/log resources using `kubectl auth can-i`
10. WHEN the pipeline runs, THE Auto_Grader SHALL validate that the `log-monitor` ServiceAccount cannot `delete` pods using `kubectl auth can-i`
11. WHEN the pipeline runs, THE Auto_Grader SHALL validate that the Python_App pod logs contain the string "SUCCESS: Found pods in namespace"
12. WHEN the pipeline runs, THE Auto_Grader SHALL deploy a test pod that generates known log lines including ERROR, WARN, and INFO severity entries
13. WHEN the pipeline runs, THE Auto_Grader SHALL deploy a deliberately crashing pod (one that enters `CrashLoopBackOff` state) alongside the Python_App
14. WHEN the pipeline runs, THE Auto_Grader SHALL expose the Python_App's HTTP endpoints via `kubectl port-forward` or a Kubernetes Service and validate the `/logs` endpoint returns valid JSON containing ERROR and WARN entries but not INFO entries
15. WHEN the pipeline runs, THE Auto_Grader SHALL validate the `/health` endpoint returns valid JSON that identifies the deliberately crashing pod as unhealthy
16. WHEN grading is complete, THE Auto_Grader SHALL report results back to the candidate's PR on the Public_Challenge_Repo by posting a PR comment or creating a check run via the GitHub API using the Cross_Repo_PAT

### Requirement 8: End-to-End Validation Workflow (Private Repo)

**User Story:** As a hiring manager, I want an end-to-end validation workflow in the private grader repo that simulates the complete candidate experience — forking, pushing code, opening a PR, and waiting for grader results — so that I can confirm the entire cross-repo dispatch chain works before sharing the public repo with candidates.

#### Acceptance Criteria

1. THE Private_Grader_Repo SHALL contain a separate GitHub Actions workflow file (`.github/workflows/validate.yml`) dedicated to end-to-end validation of the challenge
2. THE validation workflow SHALL trigger on manual dispatch (`workflow_dispatch`) so that maintainers can run the end-to-end check on demand
3. THE Private_Grader_Repo SHALL contain a `solution/` directory holding corrected versions of `terraform/main.tf`, `python/Dockerfile`, `python/app.py`, `python/requirements.txt`, `kubernetes/rbac.yaml`, and `kubernetes/deployment.yaml`
4. WHEN the validation workflow runs the happy path, it SHALL use the GitHub API to create a temporary fork of the Public_Challenge_Repo
5. WHEN the fork is created, THE validation workflow SHALL clone the fork, apply the known-good solution files from the `solution/` directory onto the fork, and push the changes to a branch on the fork
6. WHEN the solution branch is pushed, THE validation workflow SHALL open a pull request from the fork against the Public_Challenge_Repo's `main` branch
7. WHEN the PR is opened, THE validation workflow SHALL wait for the Dispatch_Workflow to fire and for the Auto_Grader in the Private_Grader_Repo to run and post results back to the PR
8. WHEN grader results are posted, THE validation workflow SHALL assert that the PR received a "pass" result by checking for a passing check run or a success comment on the PR
9. WHEN the happy path completes (pass or fail), THE validation workflow SHALL clean up by closing the PR, deleting the fork branch, and deleting the temporary fork via the GitHub API
10. WHEN the validation workflow runs the sad path, it SHALL create a temporary fork of the Public_Challenge_Repo, make a trivial change (e.g., add a comment) without applying solution fixes, push the branch, and open a PR against the Public_Challenge_Repo's `main` branch
11. WHEN the sad path PR is opened, THE validation workflow SHALL wait for the Auto_Grader to run and post results, then assert that the PR received a "fail" result
12. WHEN the sad path completes, THE validation workflow SHALL clean up by closing the PR, deleting the fork branch, and deleting the temporary fork
13. THE validation workflow SHALL use a GitHub PAT with `repo`, `delete_repo`, and `workflow` scopes stored as a secret, to perform fork creation, PR management, and fork cleanup
14. THE validation workflow SHALL implement a polling loop with a timeout of approximately 10 minutes to wait for grader results on the PR
15. THE validation workflow's happy path and sad path jobs SHALL run sequentially (sad path after happy path) to avoid race conditions on the Public_Challenge_Repo
16. IF the validation workflow's happy path does not receive a "pass" result within the timeout, THEN it SHALL exit with a non-zero status and report the failure
17. IF the validation workflow's sad path does not receive a "fail" result (or receives a "pass"), THEN it SHALL exit with a non-zero status indicating the grader is not catching issues
18. THE validation workflow SHALL use a unique branch name (e.g., including a run ID or timestamp) to avoid conflicts with concurrent runs


### Requirement 9: Cross-Repo Dispatch Workflow (Public Repo)

**User Story:** As a hiring manager, I want the public challenge repo to automatically trigger the private grader when a candidate opens a pull request, so that grading happens seamlessly without exposing grading logic.

#### Acceptance Criteria

1. THE Public_Challenge_Repo SHALL contain a GitHub Actions workflow file (`.github/workflows/dispatch.yml`) that triggers on `pull_request` events targeting the `main` branch
2. WHEN a pull request is opened or updated on the Public_Challenge_Repo, THE Dispatch_Workflow SHALL send a `repository_dispatch` event to the Private_Grader_Repo with event type `grade-submission`
3. THE Dispatch_Workflow SHALL include in the dispatch payload: the candidate's PR head repository clone URL, the PR head ref/SHA, and the PR number
4. THE Dispatch_Workflow SHALL use a Cross_Repo_PAT stored as a repository secret to authenticate the `repository_dispatch` API call to the Private_Grader_Repo
5. THE Dispatch_Workflow SHALL NOT contain any grading logic, solution files, or grading criteria — it is solely a trigger mechanism
6. WHEN the dispatch event is sent, THE Dispatch_Workflow SHALL create a pending check run or PR comment on the candidate's PR indicating that grading has been initiated
