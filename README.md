# Overview
Repository for deploying and hosting an interactive viewer application server for a WTX dataset on a ARDC Nectar research cloud project allocation.

# Main Components
1) `/ardcnectar`: Contains scripts for automated deployment onto an existing Nectar allocation.
   
2) Docker stack: Builds and runs the application running on a compute instance in the project allocation.
- `docker-compose.yml`: Defines docker stack
- `/data_config`: `data_store` service
- `/server_config`: `viewer_app` service
- `/vitessce_config`: Independent docker container to reproduce/regenerate `config.json`.

# Usage
## Initial Deployment
See `/ardcnectar/README.md`

## CI/CD
Requires initial deployment to launch instance.
CD ensures website reflects latest `/server_config/index.html` layouts and `config.json` defined by `vitessce_config/src/export_config.py`.

# Citation
tba