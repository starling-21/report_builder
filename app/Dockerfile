FROM python:3.7-slim AS base
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1



#-----------------------------
FROM base AS python-deps

ENV PIPENV_VENV_IN_PROJECT = 1

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git && \
    apt-get install -y netcat-openbsd && \
    apt-get install -y --no-install-recommends gcc && \
    apt-get clean

RUN pip install --upgrade pip && \
    pip install pipenv


COPY Pipfile .
#COPY Pipfile.lock .
RUN set -ex && pipenv install --deploy --dev



#-------------------------------------
FROM base AS runtime
#Copy virtual env from python-deps stage
COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

WORKDIR /usr/src/app
#COPY . /usr/src/app

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
#CMD []


