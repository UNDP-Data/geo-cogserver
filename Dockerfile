FROM ghcr.io/osgeo/gdal:ubuntu-small-3.11.0

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libffi-dev \
      python3-pip \
      pipenv

WORKDIR /opt/server

RUN export PYTHON_VERSION="$(python3 --version | cut -d ' ' -f 2)" && pipenv --python ${PYTHON_VERSION} --site-packages

RUN pipenv run pip install -U pip

#RUN pipenv run pip install uvicorn titiler asyncpg postgis --no-cache-dir  --upgrade
COPY requirements.txt requirements.txt
RUN pipenv run pip install -r requirements.txt
COPY src/cogserver cogserver

ENV HOST=0.0.0.0
ENV PORT=8000
ENV LOG_LEVEL=info
ENV RELOAD=--reload
ENV WORKERS=1
ENV THREADS=1
#CMD pipenv run uvicorn cogserver:app --host ${HOST} --port ${PORT} --log-level ${LOG_LEVEL} ${RELOAD}
CMD pipenv run gunicorn cogserver:app -k uvicorn.workers.UvicornWorker --workers=${WORKERS} --threads=${THREADS} --bind=${HOST}:${PORT} --log-level=${LOG_LEVEL} ${RELOAD}