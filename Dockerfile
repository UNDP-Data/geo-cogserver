FROM ghcr.io/osgeo/gdal:ubuntu-small-3.8.4 as base

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  libffi-dev python3-pip
RUN python3 -m pip install pipenv
WORKDIR /opt/server
RUN export PYTHON_VERSION="$(python3 --version | cut -d ' ' -f 2)" && pipenv --python ${PYTHON_VERSION} --site-packages
RUN pipenv run pip install -U pip
#RUN pipenv run pip install uvicorn titiler asyncpg postgis --no-cache-dir  --upgrade
COPY requirements.txt requirements.txt
RUN pipenv run pip install -r requirements.txt
COPY src/cogserver cogserver
ENV HOST=0.0.0.0
ENV PORT=8000
#ENV WEB_CONCURRENCY=1
#ENV CPL_TMPDIR=/tmp
#ENV GDAL_CACHEMAX=75%
#ENV GDAL_INGESTED_BYTES_AT_OPEN=32768
#ENV GDAL_DISABLE_READDIR_ON_OPEN=EMPTY_DIR
#ENV GDAL_HTTP_MERGE_CONSECUTIVE_RANGES=YES
#ENV GDAL_HTTP_MULTIPLEX=YES
#ENV GDAL_HTTP_VERSION=2
#ENV PYTHONWARNINGS=ignore
#ENV VSI_CACHE=FALSE
#ENV RIO_TILER_MAX_THREADS=2
ENV LOG_LEVEL=info
ENV RELOAD=--reload

#CMD pipenv run uvicorn cogserver:app --host ${HOST} --port ${PORT} --log-config cogserver/logconf.yaml
CMD pipenv run uvicorn cogserver:app --host ${HOST} --port ${PORT} --log-level ${LOG_LEVEL} ${RELOAD}
