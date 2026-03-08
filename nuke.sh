#!/bin/bash

# Stop and remove containers, networks, volumes, and images
docker-compose down --volumes --rmi all

# Remove all unused Docker objects (images, containers, volumes, networks)
docker system prune --all -f
docker volume prune

# Rebuild and start the containers
#docker-compose up --build