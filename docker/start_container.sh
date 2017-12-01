#!/bin/bash

docker run -e N="8" -e t="2" -e B="16" -v $(pwd):/root/distributed_authentication -i distributed_authentication