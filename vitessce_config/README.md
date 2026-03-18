# vitessce_config

Standalone Docker environment for generating `config.json` using the Vitessce Python API against a SpatialData `.zarr` store.

## Usage

Build the image from this directory:
```sh
docker build -t vitessce-config .
```

Run to generate `config.json` into this directory:
```sh
docker run --rm \
  -v $(pwd):/output \
  -e SPATIALDATA_URI=http://<host>/zarr \
  vitessce-config
```

`config.json` will be written to `vitessce_config/config.json` on the host.

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `SPATIALDATA_URI` | `http://viewer.nsclc-spatial-atlas.cloud.edu.au/zarr` | URL of the zarr store served by viewer_app |
| `CONFIG_PATH` | `/output` | Directory inside the container to write `config.json` |

## Deployment

During deployment, `cloud_init.yaml` builds this image and runs it automatically, injecting `SPATIALDATA_URI` from the configured `app.app_domain` in `ardcnectar/instance_config.yaml`. The generated `config.json` is then picked up by `viewer_app` during `docker compose up --build`.
