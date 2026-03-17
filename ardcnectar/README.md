# Overview
Contains deployment environment and scripts for deploying the wtx_viewer in on Nectar using OpenStack.
- Creates compute container instance
- Generates application credentials for that instance
- Registers container instance IP to project allocation zone as a record set
- Runs docker service in compute instance to host viewer application (see `data_config`, `server_config`, `vitessce_config`).

# Requirements
- Defined in pyproject.toml

# Environmental Variables
The following environmental variables need to be set:
- `OS_AUTH_URL`
- `OS_USERNAME`
- `OS_PASSWORD`
- `OS_PROJECT_ID`
- `OS_USER_DOMAIN_NAME`
- `OS_PROJECT_DOMAIN_ID`
- `OS_PROJECT_NAME`

It is recommended to set these from a `.env` file or by sourcing an OpenStack RC file (i.e. see https://tutorials.rc.nectar.org.au/openstack-cli/04-credentials).

# Usage
With user credentials and the above environmental variables run in this directory:

```{python}
uv run deploy.py
```