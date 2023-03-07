#!/bin/sh

echo "Creating Docker network and starting the DB"

NETWORK="avaaz"
if docker network inspect ${NETWORK} > /dev/null 2>&1
then
    echo "Network OK"
else
    docker network create --attachable ${NETWORK}
fi

docker compose run --name avaaz-database-dev --rm -i database-dev
