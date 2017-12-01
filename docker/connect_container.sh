#!/bin/bash

docker exec -it $(docker ps -l -q) /bin/bash
