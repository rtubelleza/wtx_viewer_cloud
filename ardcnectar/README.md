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
- 

# Usage
With user credentials and the above environmental variables set:

```{python}
uv run deploy.py
```

This will launch a compute instance running this wtx_viewer.