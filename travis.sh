#!/bin/bash

set -x

if [ "$USE_SUDO" == "" ]; then
    export USE_SUDO=true
fi

function sudo()
{
    if [ "$USE_SUDO" = "true" ]; then
        /usr/bin/sudo $@
    else
        $@
    fi
}

if [ $ROS_DISTRO == "indigo" -a "$TRAVIS_JOB_ID" ]; then
    sudo apt-get install -qq -y python-jenkins
    ./.travis/travis_jenkins.py
    exit $?
fi

function error {
    trap - ERR
    if [ "$BUILDER" == rosbuild -a -e ${HOME}/.ros/rosmake/ ]; then find ${HOME}/.ros/rosmake/ -type f -exec echo "=== {} ===" \; -exec cat {} \; ; fi
    if [ -e ${HOME}/.ros/test_results ]; then find ${HOME}/.ros/test_results -type f -exec echo "=== {} ===" \; -exec cat {} \; ; fi
    for file in ${HOME}/.ros/log/rostest-*; do echo "=== $file ==="; cat $file; done
    if [ "$BUILDER" == catkin ]; then find ~/ros/ws_$REPOSITORY_NAME/build -name LastTest.log -exec echo "==== {} ====" \; -exec cat {} \;  ; fi
    exit 1
}

trap error ERR

### before_install: # Use this to prepare the system to install prerequisites or dependencies
# Define some config vars
export CI_SOURCE_PATH=$(pwd)
export REPOSITORY_NAME=${PWD##*/}
if [ ! "$ROS_PARALLEL_JOBS" ]; then export ROS_PARALLEL_JOBS="-j8 -l8";  fi
echo "Testing branch $TRAVIS_BRANCH of $REPOSITORY_NAME"
sudo sh -c 'echo "deb http://packages.ros.org/ros-shadow-fixed/ubuntu `lsb_release -cs` main" > /etc/apt/sources.list.d/ros-latest.list'
wget http://packages.ros.org/ros.key -O - | sudo apt-key add -
lsb_release -a
sudo apt-get update
sudo apt-get install -y python-catkin-pkg python-rosdep python-wstool ros-$ROS_DISTRO-catkin ros-$ROS_DISTRO-rosbash
if [ "$ROSWS" == rosws ]; then sudo apt-get install -qq -y python-rosinstall     ; fi
if [ "$BUILDER" == rosbuild ]; then sudo apt-get install -qq -y ros-$ROS_DISTRO-rosmake ; fi
if [ "$EXTRA_DEB" ]; then sudo apt-get install -qq -y $EXTRA_DEB;  fi
# MongoDB hack - I don't fully understand this but its for moveit_warehouse
dpkg -s mongodb || echo "ok"; export HAVE_MONGO_DB=$?
if [ $HAVE_MONGO_DB == 0 ]; then sudo apt-get remove -qq -y mongodb mongodb-10gen || echo "ok"; fi
if [ $HAVE_MONGO_DB == 0 ]; then sudo apt-get install -qq -y mongodb-clients mongodb-server -o Dpkg::Options::="--force-confdef" || echo "ok"; fi # default actions
# Setup rosdep
sudo rosdep init
rosdep update; while [ $? != 0 ]; do sleep 1; rosdep update; done

### install: # Use this to install any prerequisites or dependencies necessary to run your build
# Create workspace
mkdir -p ~/ros/ws_$REPOSITORY_NAME/src
cd ~/ros/ws_$REPOSITORY_NAME/src
if [ "$USE_DEB" == false -o $BUILDER == rosbuild ]; then $ROSWS init .   ; fi
if [ "$USE_DEB" == false ]; then $ROSWS merge file://$CI_SOURCE_PATH/.rosinstall      ; fi
if [ "$USE_DEB" == false -o $BUILDER == rosbuild ]; then if [ $ROSWS == rosws ]; then $ROSWS merge /opt/ros/$ROS_DISTRO/.rosinstall; fi  ; fi
if [ "$USE_DEB" == false ]; then sed -i "s@^\(.*github.com/$TRAVIS_REPO_SLUG.*\)@#\1@" .rosinstall               ; fi # comment out current repo
if [ "$USE_DEB" == false ]; then $ROSWS update   ; fi
if [ "$USE_DEB" == false -o $BUILDER == rosbuild ]; then $ROSWS set $REPOSITORY_NAME http://github.com/$TRAVIS_REPO_SLUG --git -y        ; fi
ln -s $CI_SOURCE_PATH . # Link the repo we are testing to the new workspace
cd ../
# Install dependencies for source repos
if [ "$ROSDEP_UPDATE_QUIET" == "true" ]; then
    ROSDEP_ARGS=>/dev/null
fi
source /opt/ros/$ROS_DISTRO/setup.bash # ROS_PACKAGE_PATH is important for rosdep
${CI_SOURCE_PATH}/.travis/rosdep-install.sh


### before_script: # Use this to prepare your build for testing e.g. copy database configurations, environment variables, etc.
source /opt/ros/$ROS_DISTRO/setup.bash # re-source setup.bash for setting environmet vairable for package installed via rosdep
if [ "$BUILDER" == rosbuild ]; then source src/setup.bash        ; fi
if [ "$BUILDER" == rosbuild ]; then rospack profile              ; fi

### script: # All commands must exit with code 0 on success. Anything else is considered failure.
# for catkin
if [ "$BUILDER" == catkin ]; then catkin_make $ROS_PARALLEL_JOBS            ; fi
if [ "$BUILDER" == catkin ]; then export TARGET_PKG=`find build/$REPOSITORY_NAME -name Makefile -print |  sed s@.*/\\\\\([^\/]*\\\\\)/Makefile@\\\1@g` ; fi
if [ "$BUILDER" == catkin ]; then catkin_make test --pkg $TARGET_PKG $ROS_PARALLEL_JOBS  ; fi
if [ "$BUILDER" == catkin ]; then find build -name LastTest.log -exec echo "==== {} ====" \; -exec cat {} \;  ; fi
if [ "$BUILDER" == catkin ]; then catkin_make $ROS_PARALLEL_JOBS install            ; fi
if [ "$BUILDER" == catkin ]; then rm -fr devel src build                 ; fi
if [ "$BUILDER" == catkin ]; then source install/setup.bash              ; fi
if [ "$BUILDER" == catkin ]; then export EXIT_STATUS=0; for pkg in $TARGET_PKG; do [ "`find install/share/$pkg -iname '*.test'`" == "" ] && echo "[$pkg] No tests ware found!!!"  || find install/share/$pkg -iname "*.test" -print0 | xargs -0 -n1 rostest || export EXIT_STATUS=$?; done; [ $EXIT_STATUS == 0 ] ; fi
# for rosbuild
if [ "$BUILDER" == rosbuild ]; then rosmake --profile `find -L $CI_SOURCE_PATH | grep manifest.xml | sed s@.*/\\\\\([^\/]*\\\\\)/manifest.xml\\\$@\\\1@g` ; fi
if [ "$BUILDER" == rosbuild ]; then export TARGET_PKG=`find -L src | grep $REPOSITORY_NAME | grep /build/Makefile$ | sed s@.*/\\\\\([^\/]*\\\\\)/build/Makefile@\\\1@g` ; fi
if [ "$BUILDER" == rosbuild ]; then rosmake --test-only $TARGET_PKG ; fi
