FROM python:3.11

LABEL Author="Rafael T"
LABEL Description="Standalone container: run to generate config.json"

RUN python3 -m venv /opt/vitessce_env
ENV PATH="/opt/vitessce_env/bin:$PATH"

RUN pip install "setuptools<81"
RUN pip install "spatialdata==0.5.0"
RUN pip install "vitessce[all]"

COPY src /src
WORKDIR /src

ENV CONFIG_PATH="/output"

CMD ["python", "export_config.py"]
