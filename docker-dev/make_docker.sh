#!/bin/bash

# export UID=$(id)

docker build \
    -t schems-fun-dev:latest \
    --build-arg SHH="`wget -O - https://raw.githubusercontent.com/Godhart/schems-fun-misc-tools/main/running/migrate_schems_fun.sh | md5sum``wget -O - https://raw.githubusercontent.com/Godhart/schems-fun-misc-tools/main/running/run_schems_fun.sh | md5sum`" \
    --build-arg UID=`id -u` \
    --build-arg GID=`id -g` \
    .
