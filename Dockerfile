# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=python:3.12

#####################################################################################
# Python Base
# hadolint ignore=DL3006
FROM ${PYTHON_VERSION}-slim AS base

ARG TARGETARCH

# Python specific settings
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    VIRTUAL_ENV="/venv"

# Poetry environment variables
ENV POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VERSION=1.8.2

RUN apt-get update && \
    apt-get install -y \
    curl

# Set the path
ENV PATH="${POETRY_HOME}/bin:${VIRTUAL_ENV}/bin:${PATH}"

RUN python -m venv ${VIRTUAL_ENV}

ENV APP_DIR=/app/
WORKDIR ${APP_DIR}

ENV PYTHONPATH="${APP_DIR}:${PYTHONPATH}"

ENV APP_USER=webapp

RUN addgroup --system --gid 1000 "${APP_USER}" \
    && adduser --uid 1000 --gid 1000 "${APP_USER}" \
    && chown -R "${APP_USER}":"${APP_USER}" "${APP_DIR}"

#####################################################################################
# Install Poetry and dependencies in a build stage
FROM base AS builder
LABEL org.opencontainers.image.source=https://github.com/rewindio/github-to-slack-notifier \
    org.opencontainers.image.authors="devops@rewind.io" \
    org.opencontainers.image.stage="builder"


SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN --mount=type=cache,target=/root/.cache \
    curl -sSL https://install.python-poetry.org | python -

# Set up the working directory
WORKDIR /app
# Copy only the dependency files to take advantage of caching
COPY pyproject.toml poetry.lock ./

RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root --only main


#####################################################################################
# Stage production
FROM base AS production
LABEL org.opencontainers.image.source=https://github.com/rewindio/github-to-slack-notifier \
    org.opencontainers.image.authors="devops@rewind.io" \
    org.opencontainers.image.stage="production"

COPY --from=builder ${POETRY_HOME} ${POETRY_HOME}
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR ${APP_DIR}

COPY pyproject.toml poetry.lock ./
COPY . .

ENTRYPOINT [ "python3", "/app/src/main.py" ]
