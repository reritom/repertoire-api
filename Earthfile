VERSION 0.8

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

    # To check that migrations have been applied
    RUN apk add postgresql-client
    ENV CI=true
    RUN apk add curl
    RUN curl -sSf https://atlasgo.sh | sh

# build-repertoire-api-dev-image - Build the local deployment image
build-repertoire-api-dev-image:
    FROM +build-base
    WORKDIR /home

    COPY . .
    EXPOSE 8080
    CMD 'sh etc/scripts/await_migrations.sh || exit 1; uvicorn wsgi:app --host 0.0.0.0 --port 8080 --reload'

    SAVE IMAGE repertoire-api-dev:latest

# build-repertoire-celery-beat-dev-image - Build the local deployment image
build-repertoire-celery-beat-dev-image:
    FROM +build-base
    WORKDIR /home

    COPY . .
    EXPOSE 8080
    CMD 'sh etc/scripts/await_migrations.sh || exit 1; watchmedo auto-restart -d . -p "*.py" -R -- celery -A wsgi.celery worker -l info -B -s /tmp/celerybeat-schedule --uid=nobody --gid=nogroup'

    SAVE IMAGE repertoire-celery-beat-dev:latest

# build-repertoire-test-image - Build the test container image
build-repertoire-test-image:
    FROM +build-base
    
    # Install all deps, including dev deps
    RUN pdm sync --dev
    
    VOLUME [ "/home/app" ]
    WORKDIR /home
    CMD sh -c "tail -f /dev/null"
    SAVE IMAGE repertoire-test:latest

# test - Run the pytest suite in a container mounted on the app source
test:
    FROM earthly/dind:alpine
    WAIT
        BUILD +build-repertoire-test-image
    END

    WORKDIR /home

    # For docker compose running
    COPY etc/test/test-initdb ./test-initdb
    COPY etc/test/test-compose.yml ./test-compose.yml

    # For source (dind backend container will mount onto this copied directory)
    COPY app ./app

    ARG path="."
    ARG num="4"

    WITH DOCKER --compose test-compose.yml --load repertoire-test:latest=+build-repertoire-test-image
        RUN --no-cache docker exec -t test-backend pytest --tb=short -n $num $path -vv --durations=50
    END


# deploy-local - Deploy the application local stack
deploy-local:
    LOCALLY
    WAIT
        BUILD +build-repertoire-api-dev-image
    END

    WITH DOCKER --load repertoire-api-dev:latest=+build-repertoire-api-dev-image --load repertoire-migrator:latest=+build-repertoire-migrator-image --load repertoire-celery-beat-dev:latest=+build-repertoire-celery-beat-dev-image
        RUN docker compose -f etc/local/local-compose.yml up
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


# build-openapi-json - [Internal] Build the app openapi.json and save as an artifact
build-openapi-json:
    FROM earthly/dind:alpine

    WORKDIR /home
    COPY . .

    WITH DOCKER --compose etc/docs/docgen-compose.yaml --load repertoire-api-dev:latest=+build-repertoire-api-dev-image
        # Generate the openapi which will be saved in a mounted volume
        RUN docker exec -t repertoire-api-dev python -m app.cli generate-openapi /home/built-artifacts/openapi.json
    END

    SAVE ARTIFACT /home/built-artifacts/openapi.json

# build-repertoire-redoc - Build the repertoire redoc image
build-repertoire-redoc:
    FROM redocly/redoc:latest
    COPY +build-openapi-json/openapi.json /usr/share/nginx/html/spec.json
    ENV SPEC_URL=spec.json
    SAVE IMAGE repertoire-redoc:latest

# deploy-docs-local - Deploy the redoc image locally
deploy-docs-local:
    LOCALLY

    WITH DOCKER --load repertoire-redoc:latest=+build-repertoire-redoc
        RUN docker-compose -f etc/docs/docs-compose.yaml up
    END

# init-local-database - Create the database and tables for a fresh local deployment
init-local-database:
    LOCALLY
    RUN docker exec -t repertoire-api-dev python -m app.cli init-db

# create-local-user - Create a user on the local deployed instance
create-local-user:
    LOCALLY
    ARG --required email
    ARG --required password
    RUN docker exec -t repertoire-api-dev python -m app.cli accounts create-user --email=$email --password=$password

# run-bruno-suite - Run a specific bruno test folder against a ephemeral instance of the backend, example argument: --SUITE=tests/authentication/login 
run-bruno-suite:
    FROM earthly/dind:alpine
    RUN apk add --update nodejs npm
    RUN npm install -g @usebruno/cli
    ARG --required SUITE
    COPY . .

    WITH DOCKER --compose etc/local/local-compose.yml --load repertoire-api-dev:latest=+build-repertoire-api-dev-image --load repertoire-migrator:latest=+build-repertoire-migrator-image --load repertoire-celery-beat-dev:latest=+build-repertoire-celery-beat-dev-image
        RUN sleep 10 && \ # TODO make an "await-api script"
            docker exec -t repertoire-api-dev python -m app.cli accounts create-user --email=test@test.test --password=test1 && \
            cd bruno && \
            bru run $SUITE --env local
    END

# run-all-bruno-suites - Run all bruno test folders. Each folder will be tested against it's own ephemeral instance of the backend
run-all-bruno-suites:
    LOCALLY
    # Iterate all leaf directories within the bruno test directory
    WORKDIR bruno
    FOR suite IN $(find tests/* -type d | sort | awk '$0 !~ last "/" {print last} {last=$0} END {print last}')
        IF [ -z "$( ls -A $suite )" ]
            RUN echo "Skipping $suite as it is empty"
        ELSE
            BUILD +run-bruno-suite --SUITE=$suite
        END
    END

# atlas-base - [Internal] Base image for migration flows
atlas-base:
    FROM earthly/dind:alpine

    WORKDIR /home

    ENV CI=true
    RUN apk add curl
    RUN curl -sSf https://atlasgo.sh | sh

    COPY atlas.hcl atlas.hcl
    COPY migrations migrations

# generate-atlas-hcl - [Internal] Generate the target schema of the database (atlas hcl format)
generate-atlas-hcl:
    FROM +atlas-base

    COPY . .

    # Deploy the local stack
    WITH DOCKER --compose etc/hcl/hcl-compose.yml --load repertoire-api-dev:latest=+build-repertoire-api-dev-image
        # Populate the database based on the local code definitions
        # Then use atlas to create a hcl file based on the local state
        RUN docker exec -t repertoire-api-dev python -m app.cli init-db && \
            atlas schema inspect -u "postgres://one:password@localhost:5432/repertoire?sslmode=disable" > schema.hcl
    END

    SAVE ARTIFACT schema.hcl

# generate-migration-internal - [Internal] Generate a new migration and save the updated migrations directory as an artifact
generate-migration-internal:
    FROM +atlas-base

    ARG --required name

    COPY +generate-atlas-hcl/schema.hcl schema.hcl

    WITH DOCKER
        RUN atlas migrate diff $name \
            --dir "file://migrations" \
            --to "file://schema.hcl" \
            --dev-url "docker://postgres/16/dev?search_path=public"
    END

    SAVE ARTIFACT migrations


# generate-migration - Generate a new migration and overwrite migrations directory
generate-migration:
    FROM +atlas-base
    ARG --required name

    COPY (+generate-migration-internal/migrations --name=$name) migrations
    SAVE ARTIFACT migrations AS LOCAL migrations

# build-repertoire-migrator-image - Build an ephemeral image that will apply the migrations to the target db
build-repertoire-migrator-image:
    FROM +atlas-base
    RUN apk add postgresql-client
    CMD 'pg_isready -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -d ${POSTGRES_DATABASE} || exit 1; atlas migrate apply --url postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}/${POSTGRES_DATABASE}?sslmode=disable'
    SAVE IMAGE repertoire-migrator:latest

# check-migrations-created - Check that no new migrations need to be made
check-migrations-created:
    FROM +atlas-base
    RUN apk add git

    WORKDIR /home/migrations
    LET initialCount = $(ls -1 | wc -l)
    WORKDIR /home

    COPY (+generate-migration-internal/migrations --name=dummymigration) migrations

    WORKDIR /home/migrations
    LET newCount = $(ls -1 | wc -l)
    RUN [ "$newCount" == "$initialCount" ] || { echo "Migrations need to be created" && exit 1; };

# lint-migrations - Check that the migrations follow the rules
lint-migrations:
    FROM +atlas-base

    WITH DOCKER
        RUN atlas migrate lint --latest 1 \
            --dir "file://migrations" \
            --dev-url "docker://postgres/16/dev?search_path=public"
    END