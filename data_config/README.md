# Overview
Runs an nginx server to host an intermediate data store service. Fetches the data for the viewer from an object store using the openstack swift api.

# Components
- Dockerfile: uses base nginx image. Setup and run data_store service with `entrypoint.sh`
- nginx.conf: Reverse proxy config for data_store. Proxies `/data/zarr/` requests to the SWIFT object store.
- entrypoint.sh: Bootstraps script which validates required credentials for container instance, fetches swift token to access object store from the container instance this service is being run on. Periodically refresh token.