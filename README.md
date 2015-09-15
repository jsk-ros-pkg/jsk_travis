# jsk_travis

[![Join the chat at https://gitter.im/jsk-ros-pkg/jsk_travis](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/jsk-ros-pkg/jsk_travis?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Build Status](https://travis-ci.org/jsk-ros-pkg/jsk_travis.svg?branch=master)](https://travis-ci.org/jsk-ros-pkg/jsk_travis)

- How to update docker image on jenkins
```
echo -e "FROM ros-ubuntu:14.04\nRUN apt-get update\nRUN apt-get -y upgrade\nEXPOSE 22" | sudo docker build -t ros-ubuntu:14.04 -
```


----------------------------------------------------------


jsk_travis is a package to test ROS repositories on travis and jenkins.
In order to test on hydro, it uses travis and on indigo and jade, it uses jenkins.
The jenkins server is available on [jenkins.jsk.imi.i.u-tokyo.ac.jp](https://jenkins.jsk.imi.i.u-tokyo.ac.jp:8080).

## Restarting tests
see [this document](https://github.com/jsk-ros-pkg/jsk_common#restart-travis-from-slack)

## Environmental Variables
* `ROS_DISTRO` (required)

  Specify your target distribution of ROS. Now we support hydro, indigo and jade.
  If you specify indigo or jade, tests automatically run on jenkins.

* `USE_JENKINS` (default: `false`)

  Force to run test on jenkins. jenkins server is more powerful than travis environment, so we can use jenkins to compile pcl-related packages such as [jsk_recognition](https://github.com/jsk-ros-pkg/jsk_recognition.git).
* `NO_SUDO` (default: `false`)

  `NO_SUDO` expects to be run with `USE_JENKINS=true` and this option is required to run test with [container-based travis environment](http://docs.travis-ci.com/user/workers/container-based-infrastructure/).
