# jsk_travis

[![Join the chat at https://gitter.im/jsk-ros-pkg/jsk_travis](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/jsk-ros-pkg/jsk_travis?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Build Status](https://travis-ci.org/jsk-ros-pkg/jsk_travis.svg?branch=master)](https://travis-ci.org/jsk-ros-pkg/jsk_travis)

- How to update docker image on jenkins
```
echo -e "FROM ros-ubuntu:14.04\nRUN apt-get update\nRUN apt-get -y upgrade\nEXPOSE 22" | sudo docker build -t ros-ubuntu:14.04 - 
```
