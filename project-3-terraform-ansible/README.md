# Project 3: Full Infrastructure Automation (Terraform + Ansible + Docker)

## Overview
A single-command, end-to-end infrastructure pipeline: `terraform apply` provisions a brand-new AWS EC2 instance, waits for it to become reachable, then automatically hands off to Ansible — which installs Docker, pulls the application code, and brings the app live. No manual SSH, no manual configuration.

## Architecture

```mermaid
flowchart LR
    A[terraform apply] --> B[Provision EC2 + Security Group + Key Pair]
    B --> C[Wait for SSH readiness]
    C --> D[Trigger Ansible Playbook automatically]
    D --> E[Install Docker + Git]
    E --> F[Clone app repo from GitHub]
    F --> G[docker compose up -d]
    G --> H[App live and verified]
```

## Tech Stack
- **Infrastructure as Code**: Terraform (AWS provider)
- **Configuration Management**: Ansible
- **Provisioned Resource**: AWS EC2 (Amazon Linux, latest AMI auto-discovered), Security Group, SSH Key Pair
- **Application**: The same Dockerized notes app built and versioned in Project 1

## What Happens on `terraform apply`
1. **Provision** — Terraform creates a security group (SSH + app port), registers an SSH key pair, and launches an EC2 instance with a 20GB root volume (sized to comfortably hold Docker images).
2. **Wait for readiness** — A `remote-exec` provisioner blocks until SSH is actually accepting connections, avoiding race conditions with `local-exec` firing too early.
3. **Automatic handoff to Ansible** — A `local-exec` provisioner runs `ansible-playbook` against the new instance's public IP the moment it's reachable — no manual step in between.
4. **Configuration & Deployment (Ansible)**:
   - Installs Docker and Git
   - Installs the Docker Compose CLI plugin (not bundled by default on Amazon Linux)
   - Clones the application repository
   - Runs `docker compose up -d --build`
   - Polls the app's HTTP endpoint until it returns `200 OK`, confirming a successful deployment

## Key Engineering Decisions & Problems Solved
- **Terraform → Ansible handoff**: Chose `local-exec` + `remote-exec` provisioners over a separate manual step, so the entire pipeline runs from a single `terraform apply` — closer to how real infrastructure pipelines are wired (Terraform for provisioning, Ansible for configuration, triggered together).
- **IAM least privilege**: Used a dedicated IAM user scoped to EC2 and ECR permissions rather than root credentials, following AWS security best practice.
- **Disk sizing from experience**: Explicitly set a 20GB root volume after discovering that default 8GB volumes run out of space pulling Docker images (MySQL alone is 500MB+) — a real constraint hit and fixed during earlier stages of this project set.
- **Dynamic AMI lookup**: Used a Terraform data source to always fetch the latest Amazon Linux AMI instead of hardcoding an ID that would go stale.

## Project Structure
```
project-3-terraform-ansible/
├── main.tf                # Provider, security group, key pair, EC2 instance, provisioners
├── variables.tf           # Region, instance type, key paths
└── ansible/
    └── playbook.yml       # Docker install + app deployment
```

## How to Run It Yourself
```bash
terraform init
terraform plan
terraform apply
```
Outputs the new instance's public IP and a direct URL to the live app.

## Cleanup
```bash
terraform destroy
```
Tears down every provisioned resource (instance, security group, key pair) to avoid ongoing AWS charges.

## Result
Infrastructure and application deployment are now fully codified and reproducible — a new environment can be stood up from scratch, identically, in minutes, with zero manual intervention.
