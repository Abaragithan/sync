#!/bin/bash

# 1. Allow Docker to use the screen
xhost +local:docker > /dev/null

# 2. Run the container
sudo docker run -it --rm \
    --network host \
    -v $(pwd):/app:z \
    sync \
    /bin/bash