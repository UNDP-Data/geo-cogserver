FROM ghcr.io/osgeo/gdal:ubuntu-small-latest as base

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  libffi-dev python3-pip
RUN python3 -m pip install pipenv
WORKDIR /opt/server
RUN export PYTHON_VERSION="$(python3 --version | cut -d ' ' -f 2)" && pipenv --python ${PYTHON_VERSION}
RUN pipenv run pip install -U pip
RUN pipenv run pip install uvicorn titiler asyncpg postgis --no-cache-dir  --upgrade



COPY src/cogserver cogserver
CMD pipenv run uvicorn cogserver:app --host ${HOST} --port ${PORT}
