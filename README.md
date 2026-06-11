<p align="center">
    <img width="50%" alt="logo-nairr-dashboard" src="https://github.com/user-attachments/assets/f4fb05a6-db0c-489a-977b-44665da9e585" />
</p>

![License](https://img.shields.io/github/license/pegasus-isi/nairr-readiness-ci.svg?logo=apache&color=blue&label=License)
![Contributors](https://img.shields.io/github/contributors-anon/pegasus-isi/nairr-readiness-ci?color=green&label=Contributors)

## Setup

### ACCESS Setup

#### Create an ACCESS Account

#### Create an ACCESS Allocation

#### Setup each resource

- Anvil
- Bridges
- Expanse

### Install GitLab

#### Create GitLab CI/CD Runners

- Anvil
- Bridges
- Expanse

#### Create GitLab Variables

> [!NOTE]
> glab -R pegasus/nairr-readiness-ci variable list

KEY                           PROTECTED  MASKED  HIDDEN  EXPANDED  SCOPE  DESCRIPTION

ACCESS_PROJECT_ID               true       false   false   false     *      ACCESS allocation project id
ACCESS_SSH_USER                 true       false   false   false     *      ACCESS user's username
ACCESS_SSH_KEY_FILE             true       false   false   false     *      ACCESS user's private key file
ACCESS_GITLAB_RUNNER_CONFIG     false      false   false   true      *      ACCESS GitLab runner config.toml
ACCESS_GITLAB_RUNNER_TOKEN      true       true    true    false     *      ACCESS GitLab runner token
ACCESS_GITLAB_RUNNER_ID         false      false   false   false     *      ACCESS GitLab runner integer identifier
ACCESS_GITLAB_RUNNER_UID        false      false   false   false     *      ACCESS GitLab runner unique identifier

NAIRR_DB_HOST                   true       false   false   false     *      NAIRR MySQL database host
NAIRR_DB_PORT                   true       false   false   false     *      NAIRR MySQL database port number
NAIRR_DB_USER                   true       false   false   false     *      NAIRR MySQL database username
NAIRR_DB_PASS                   true       true    true    false     *      NAIRR MySQL database password
NAIRR_DB_NAME                   true       false   false   false     *      NAIRR MySQL database name

GITLAB_URL                      false      false   false   false     *      GitLab URL

ANVIL_SSH_USER                  true       false   false   false     *      Anvil SSH user
ANVIL_SSH_KEY_FILE              true       false   false   false     *      Anvil user's private key file
ANVIL_GITLAB_RUNNER_CONFIG      false      false   false   true      *      Anvil GitLab runner config.toml
ANVIL_GITLAB_RUNNER_TOKEN       true       false   false   false     *      Anvil GitLab runner token
ANVIL_GITLAB_RUNNER_ID          false      false   false   false     *      Anvil GitLab runner integer identifier
ANVIL_GITLAB_RUNNER_UID         false      false   false   false     *      Anvil GitLab runner unique identifier

BRIDGES_SSH_USER                true       false   false   false     *      Bridges SSH user
BRIDGES_SSH_KEY_FILE            true       false   false   false     *      Bridges user's private key file
BRIDGES_GITLAB_RUNNER_CONFIG    false      false   false   true      *      Bridges GitLab runner config.toml
BRIDGES_GITLAB_RUNNER_TOKEN     true       true    true    false     *      Bridges GitLab runner token
BRIDGES_GITLAB_RUNNER_ID        false      false   false   false     *      Bridges GitLab runner integer identifier
BRIDGES_GITLAB_RUNNER_UID       false      false   false   false     *      Bridges GitLab runner unique identifier

DELTA_GITLAB_RUNNER_TOKEN       true       true    true    false     *      Delta GitLab runner token
DELTA_GITLAB_RUNNER_ID          false      false   false   false     *      Delta GitLab runner integer identifier
DELTA_GITLAB_RUNNER_UID         false      false   false   false     *      Delta GitLab runner unique identifier

DELTA_AI_GITLAB_RUNNER_TOKEN    true       true    true    false     *      Delta AI GitLab runner token
DELTA_AI_GITLAB_RUNNER_ID       false      false   false   false     *      Delta AI GitLab runner integer identifier
DELTA_AI_GITLAB_RUNNER_UID      false      false   false   false     *      Delta AI GitLab runner unique identifier

EXPANSE_SSH_USER                true       false   false   false     *      Expanse SSH user
EXPANSE_SSH_MFA_SHARED_SECRET   true       true    true    false     *      Expanse user's MFA shared secret
EXPANSE_SSH_KEY_FILE            true       false   false   false     *      Expanse user's private key file
EXPANSE_GITLAB_RUNNER_CONFIG    false      false   false   true      *      Expanse GitLab runner config.toml
EXPANSE_GITLAB_RUNNER_TOKEN     true       true    true    false     *      Expanse GitLab runner token
EXPANSE_GITLAB_RUNNER_ID        false      false   false   false     *      Expanse GitLab runner integer identifier
EXPANSE_GITLAB_RUNNER_UID       false      false   false   false     *      Expanse GitLab runner unique identifier

STAMPEDE3_SSH_USER              true       false   false   false     *      Stampede 3 SSH user
STAMPEDE3_SSH_MFA_SHARED_SECRET true       true    true    false     *      Stampede 3 user's MFA shared secret
STAMPEDE3_SSH_KEY_FILE          true       false   false   false     *      Stampede 3 user's private key file
STAMPEDE3_GITLAB_RUNNER_CONFIG  false      false   false   true      *      Stampede 3 GitLab runner config.toml
STAMPEDE3_GITLAB_RUNNER_TOKEN   true       true    true    false     *      Stampede 3 GitLab runner token
STAMPEDE3_GITLAB_RUNNER_ID      false      false   false   false     *      Stampede 3 GitLab runner integer identifier
STAMPEDE3_GITLAB_RUNNER_UID     false      false   false   false     *      Stampede 3 GitLab runner unique identifier

## References

- [Pegasus Workflow Management System](https://pegasus.isi.edu)

## Funding

The NAIRR readiness CI is funded by National Science Foundation (NSF) under award [22138286403051](https://www.nsf.gov/awardsearch/showAward?AWD_ID=2138286).
