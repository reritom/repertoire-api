#!/bin/sh

# This script will exit 1 if the database or migrations are not ready
# Requires atlas and pg_isready
# Requires env vars for the postgres host:
#   POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DATABASE, POSTGRES_USER, POSTGRES_PASSWORD
# And should be run from a directory that contains a "migrations" directory

echo "Checking if database is ready"
pg_isready -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -d ${POSTGRES_DATABASE}
if [ $? -eq 1 ];
then
    echo "Postgres is not ready";
    exit 1
fi

atlas migrate status --url postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}/${POSTGRES_DATABASE}?sslmode=disable > status;
echo "Atlas status output is..."
cat status;
grep -q OK status;
if [ $? -eq 1 ];
then
    echo "Migrations not ready, exitting";
    exit 1
else
    echo "Migrations are ready";
    exit 0
fi
