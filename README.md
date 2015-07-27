# jsk_travis
[![Build Status](https://travis-ci.org/jsk-ros-pkg/jsk_travis.svg?branch=master)](https://travis-ci.org/jsk-ros-pkg/jsk_travis)

- How to update docker image on jenkins
```
echo -e "FROM ros-ubuntu:14.04\nRUN apt-get update\nRUN apt-get -y upgrade\nEXPOSE 22" | sudo docker build -t ros-ubuntu:14.04 - 
```
