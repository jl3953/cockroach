#!/usr/bin/env bash

if [[ ! -e /data ]]; then
    sudo mkdir /data;
fi

if [[ $(! mount -l | grep /data) != *data* ]]; then
    sudo mount -t tmpfs -o size=32g tmpfs /data
fi
