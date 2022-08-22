# syntax=docker/dockerfile:1.2

FROM --platform=linux/amd64 python:3.10-slim

ARG APP_PORT=8000
WORKDIR /app

COPY poetry.lock /app
COPY pyproject.toml /app

RUN pip install poetry==1.1.12
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi

COPY coredns_ctl /app/coredns_ctl

EXPOSE ${APP_PORT}

CMD uvicorn coredns_ctl.app:app --host 0.0.0.0