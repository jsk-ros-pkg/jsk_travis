#!/bin/bash

. $(dirname "${BASH_SOURCE[0]}")/travis_utils.sh

travis_time_start setup_docker

export DEBIAN_FRONTEND=noninteractive

if [ "$(which sudo)" = "" ]; then
  # check if archive.ubuntu.com is available in this distribution
  apt-get -y -qq update || if [ $? -eq 100 ]; then sed -i 's/archive.ubuntu.com/old-releases.ubuntu.com/g' /etc/apt/sources.list; apt-get -y -qq update; fi
  apt-get -y -qq install sudo
fi

# install fundamental packages
sudo -E apt-get -y -qq update
sudo -E apt-get -y -qq install apt-utils build-essential curl git lsb-release wget
# 20.04 does not have pip, so install get-pip.py
sudo -E apt-get -y -qq install python-pip python-setuptools || (sudo -E apt-get -y -qq install python; curl https://bootstrap.pypa.io/pip/2.7/get-pip.py | sudo -E python; sudo -E apt-get -y -qq install python3-pip)

# add user for testing
adduser --disabled-password --gecos "" travis
adduser travis sudo
chown -R travis:travis $HOME
echo "travis ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers

# check display
sudo -E apt-get -y -qq install mesa-utils
glxinfo | grep GLX

# set up apt-cache docker
echo 'Acquire::http {proxy "http://172.17.0.1:3142"; };' | sudo tee /etc/apt/apt.conf.d/02proxy.conf
# to fix https://github.com/jsk-ros-pkg/jsk_travis/pull/388#issuecomment-549735323
# see https://matoken.org/blog/2019/07/19/direct-access-to-https-repository-with-apt-cacher-ng/
# see https://github.com/sameersbn/docker-apt-cacher-ng/tree/3.1#usage
echo 'Acquire::https {proxy "false"; };' | sudo tee -a /etc/apt/apt.conf.d/02proxy.conf

# ensure setting testing environment same as travis
export USE_JENKINS=false
export USE_TRAVIS=true

travis_time_end

# run tests
su travis -c 'cd $CI_SOURCE_PATH; source .travis/travis.sh'
