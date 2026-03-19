# NAIRR Readiness CI

## Project Overview

Continuous integration system for testing SSH connectivity and infrastructure readiness across NSF ACCESS HPC clusters. Part of the Pegasus Workflow Management System ecosystem.

- **Purpose**: Automated SSH connectivity monitoring across multiple HPC systems
- **Funding**: NSF award 22138286403051
- **Repository**: https://github.com/pegasus-isi/nairr-readiness-ci

## Architecture

GitLab CI/CD pipeline running SSH connectivity tests in Rocky Linux 9 Docker containers. Results stored in MySQL database.

**Pipeline Stages**:
- `unit`: SSH connectivity tests
- `e2e`: End-to-end tests (not yet implemented)

## Directory Structure

```
.gitlab/
  ci/
    access/        # Per-resource CI job configs
      main.yml     # Orchestration — includes resource configs
      anvil.yml    # Anvil @ Purdue
      delta.yml    # Delta @ NCSA
      delta-ai.yml # Delta AI @ NCSA
      expanse.yml  # Expanse @ SDSC
    tests/
      ssh.yml      # Reusable SSH job template (.ssh-job)
.gitlab-ci.yml     # Main pipeline entrypoint
```

## HPC Resources Tested

| Resource    | Host                               | Notes                        |
|-------------|------------------------------------|------------------------------|
| Anvil        | anvil.rcac.purdue.edu             | Key-based auth               |
| Delta        | login.delta.ncsa.illinois.edu     | Via jump host                |
| Delta AI     | dtai-login.delta.ncsa.illinois.edu| Via jump host                |
| Expanse      | login.expanse.sdsc.edu            | TOTP MFA required            |

**Jump Host**: pegasus.access-ci.org (ACCESS gateway)

## SSH Job Template Variables

Defined in `.gitlab/ci/tests/ssh.yml`. Key variables for each resource job:

- `JUMP_HOST`, `JUMP_USER`, `JUMP_SSH_KEY` — bastion/proxy config
- `TARGET_HOST`, `TARGET_USER`, `TARGET_SSH_KEY` — destination host
- `TOTP_SECRET` — for MFA-protected resources (e.g., Expanse)
- `SSH_OPTIONS` — additional SSH flags
- `DB_*` — MySQL connection variables for storing results

## Test Execution Flow

1. Install tools: `openssh-clients`, `mysql`, `sshpass`, `pyotp`
2. Configure SSH keys and known hosts
3. Generate TOTP if MFA required (`pyotp`)
4. SSH through jump host to target resource
5. Record PASS/FAIL result in MySQL `readiness_results` table

## CI Variables (GitLab Secrets)

The following must be set as masked CI/CD variables in GitLab:
- SSH private keys for jump host and each resource
- `TOTP_SECRET` for MFA resources
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` for MySQL
