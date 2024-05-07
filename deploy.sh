#!/bin/bash

git pull
docker build -t flask-image-resize:latest .
docker compose up -d
docker rmi $(docker images --filter 'dangling=true' -q --no-trunc)
