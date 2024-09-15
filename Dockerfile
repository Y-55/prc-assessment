FROM python:3.11-slim

RUN apt-get update
RUN apt-get install curl gcc build-essential -y

RUN ARCH=$(dpkg --print-architecture) && \
    if [ "$ARCH" = "arm64" ]; then \
        curl -OL https://golang.org/dl/go1.21.0.linux-arm64.tar.gz && \
        tar -C /usr/local -xzf go1.21.0.linux-arm64.tar.gz; \
    else \
        curl -OL https://golang.org/dl/go1.21.0.linux-amd64.tar.gz && \
        tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz; \
    fi

# Add Go and GOBIN to PATH
ENV GOPATH=/go \
    GOBIN=$GOPATH/bin \
    PATH="/usr/local/go/bin:$GOBIN:$PATH"

# Install goose and make sure it's in PATH
RUN go install github.com/pressly/goose/v3/cmd/goose@latest && \
    ln -s $GOBIN/goose /usr/local/bin/goose

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_HOME="/opt/poetry" \
    GOOSE_DRIVER=clickhouse \
    GOOSE_DBSTRING="clickhouse://default:@clickhouse:9000/default"

RUN pip install poetry==1.8

ENV PATH="$POETRY_HOME/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"



WORKDIR /app

COPY ./pyproject.toml /app/pyproject.toml

RUN poetry install

