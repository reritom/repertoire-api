VERSION 0.7

# deps-base - [Internal] build the base layers for pdm related targets
deps-base:
    FROM python:3.11-alpine

    # Used by dependencies from github
    RUN apk add git

    # Temp for installing pydantic-core directly
    RUN apk add rust cargo
 
    RUN pip install pdm

    COPY pyproject.toml pdm.lock ./

# build-deps - Build and save an updated pdm.lock
build-deps:
    FROM +deps-base
    RUN pdm lock --strategy no_cross_platform

    SAVE ARTIFACT pdm.lock AS LOCAL pdm.lock

# check-deps - Check that the pdm.lock has been generated for then current pyproject.toml deps
check-deps:
    FROM +deps-base
    RUN pdm lock --check

# build-base - [Internal] Build the base layers for the deployment and test images
build-base:
    FROM python:3.11-alpine

    # set environment variables to not buffer stdout/stderr, and need to create bytecode in containers
    ENV PYTHONDONTWRITEBYTECODE 1
    ENV PYTHONUNBUFFERED 1

    # required binaries
    RUN apk add alpine-sdk
    RUN apk add bash
    RUN apk update
    RUN apk add postgresql-dev gcc python3-dev musl-dev postgresql-client
    RUN pip install pdm

    # Temp for installing pydantic-core directly
    RUN apk add rust cargo

    RUN python -m venv .venv
    ENV VIRTUAL_ENV /.venv
    ENV PATH /.venv/bin:$PATH

    # Required python deps
    COPY pyproject.toml pdm.lock ./
    RUN pdm sync --prod

# build - Build then deployment image
build:
    FROM +build-base
    WORKDIR /home

    COPY . .
    EXPOSE 8080
    CMD uvicorn wsgi:app --host 0.0.0.0 --port 8080 --reload
    SAVE IMAGE repertoire:latest

# build-test - Build the test container image
build-test:
    FROM +build-base
    
    # Install all deps, including dev deps
    RUN pdm sync --dev
    
    VOLUME [ "/home/app" ]
    WORKDIR /home
    CMD sh -c "tail -f /dev/null"
    SAVE IMAGE repertoire-test:latest

# deploy - Deploy the application local stack
deploy:
    LOCALLY
    WAIT
        BUILD +build
    END

    WITH DOCKER --load repertoire:latest=+build
        RUN docker run -p 8080:8080 repertoire:latest
    END

# format - Run ruff format on the source
format:
    FROM python:3.11-alpine
    RUN pip install ruff==0.1.2
    COPY ./app /home/app
    WORKDIR /home
    RUN ruff format ./app
    RUN ruff ./app --fix
    SAVE ARTIFACT app AS LOCAL app

# lint-ruff - Run ruff check on the source
lint-ruff:
    FROM python:3.11-alpine
    RUN pip install ruff==0.1.2
    COPY . /home
    WORKDIR /home
    RUN ruff .
    RUN ruff format --check .

# lint - Run ruff on the source
lint:
    BUILD +lint-ruff
