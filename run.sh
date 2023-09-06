#!/bin/bash

if [[ ! $(docker volume ls -q | grep mariadb) ]]; then
  echo Creating Docker volume for mariadb-database...
  docker volume create mariadb-database
else
  echo Using existing mariadb-database volume.
fi
echo Done.

# Choose the container image version:
APVERSION='2.0.2'

# Bind mount root:
DATADIR=$(pwd)/../emg/data

# Change these if you already have other services running on default ports
WEBPORT=8080
VNCPORT=5901
DBPORT=3306

echo "Creating data directory ${DATADIR} if it does not already exist.."
mkdir -p $DATADIR

docker run --detach --tty \
  --volume $DATADIR:/emg/data \
  --volume mariadb-database:/var/lib/mysql \
  --volume $(pwd):/local_data \
  --volume $(pwd)/config/httpd.conf:/etc/httpd/conf/httpd.conf \
  --publish 0.0.0.0:$WEBPORT:80 --publish 0.0.0.0:$VNCPORT:5901 --publish 0.0.0.0:$DBPORT:3306 \
  --dns=8.8.8.8 \
  gitlab.chpc.utah.edu:5050/chpc/projects/appion-protomo:$APVERSION

echo Waiting for database...
sleep 10
echo Done.


