# Overview
Contains an environment and script for creating a Vitessce `config.json` using the Python API, operating on SpatialData .zarr objects.

# Usage
Set `CONFIG_PATH` to define the parent directory to store `config.json`. By default, `CONFIG_PATH` is set to the parent directory of /src.

Run:
```{python}
uv run src/export_config.py
```
