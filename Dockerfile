FROM ghcr.io/osgeo/gdal:ubuntu-small-latest as base

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  libffi-dev python3-pip
RUN python3 -m pip install pipenv
WORKDIR /opt/server
RUN export PYTHON_VERSION="$(python3 --version | cut -d ' ' -f 2)" && pipenv --python ${PYTHON_VERSION}
RUN pipenv run pip install -U pip
#RUN pipenv run pip install uvicorn titiler asyncpg postgis --no-cache-dir  --upgrade
COPY requirements.txt requirements.txt
RUN pipenv run pip install -r requirements.txt
COPY src/cogserver cogserver
ENV HOST=0.0.0.0
ENV PORT=80
ENV WEB_CONCURRENCY=2
ENV CPL_TMPDIR=/tmp
ENV GDAL_CACHEMAX=75%
ENV GDAL_INGESTED_BYTES_AT_OPEN=32768
ENV GDAL_DISABLE_READDIR_ON_OPEN=EMPTY_DIR
ENV GDAL_HTTP_MERGE_CONSECUTIVE_RANGES=YES
ENV GDAL_HTTP_MULTIPLEX=YES
ENV GDAL_HTTP_VERSION=2
ENV PYTHONWARNINGS=ignore
ENV VSI_CACHE=TRUE
ENV RIO_TILER_MAX_THREADS=2



CMD pipenv run uvicorn cogserver:app --host ${HOST} --port ${PORT} --log-config cogserver/logconf.yaml
