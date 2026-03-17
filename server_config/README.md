# Overview
Runs an nginx server to host the viewer application.

# Components
- Dockerfile: uses base nginx image. Serves `index.html`. Uses the `config.json` from `vitessce_config`.
- index.html: Entry point using React and Vitessce component to fetch + load `config.json` as runtime configuration to render the Vitessce viewer.
- nginx.conf: Reverse proxy + static server config for viewer. Serves `index.html`, proxies `/zarr` requests to the `data_store` service (see `data_config`).