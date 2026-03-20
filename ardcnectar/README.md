# Overview
Contains deployment environment and scripts for deploying the wtx_viewer in on Nectar using OpenStack.
- Creates compute container instance
- Generates application credentials for that instance
- Registers container instance IP to project allocation zone as a record set
- Runs docker service in compute instance to host viewer application (see `data_config`, `server_config`, `vitessce_config`).

# Requirements
- Defined in pyproject.toml

# Environment Variables
The following environmental variables need to be set for authentication:
| Variable | Description |
|---|---|
| `OS_AUTH_URL` | OpenStack Authentication URL. For Nectar Project allocations this is usually https://identity.rc.nectar.org.au/v3/|
| `OS_USERNAME` | OpenStack username/email. Usually member/tenantmember role. |
| `OS_PASSWORD` | OpenStack password. |
| `OS_PROJECT_ID` | OpenStack project ID for the allocation. |
| `OS_USER_DOMAIN_NAME` | OpenStack user domain name. Usually "Default". |
| `OS_PROJECT_DOMAIN_ID` | OpenStack project domain id. Usually "default". |
| `OS_PROJECT_NAME` | OpenStack project name. Usually the same name as the Nectar project allocation. |

It is recommended to set these automatiaclly from a `.env` file or by sourcing an OpenStack RC file (i.e. see https://tutorials.rc.nectar.org.au/openstack-cli/04-credentials).

# Usage

Setup UV project
```{python}
uv venv
```

a) Run deployment script:
```{python}
uv run deploy.py
```

b) The instances, application credentials, key pairs and DNS record sets created by `deploy.py` can be 'reverted' with an accompanying teardown script:
```{python}
uv run teardown.py
```