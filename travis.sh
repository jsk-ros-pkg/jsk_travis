#!/bin/bash

set -x

if [ "$ROS_DISTRO" == "indigo" -a "$TRAVIS_JOB_ID" ]; then
    sudo apt-get install -y -qq python-pip
    sudo pip install python-jenkins
    ./.travis/travis_jenkins.py
    exit $?
fi

function error {
    trap - ERR
    if [ "$BUILDER" == catkin ]; then (cd ~/ros/ws_$REPOSITORY_NAME/; catkin_test_results --all); fi
    if [ "$BUILDER" == catkin ]; then find ~/ros/ws_$REPOSITORY_NAME/build/*/test_results -type f -exec echo "==== {} ====" \; -exec cat {} \;  ; fi
    exit 1
}

[ "$BUILDER" == rosbuild ] && ( echo "$BUILDER is no longer supported"; exit 1; )
[ "$ROSWS" == rosws ] && ( echo "$ROSWS is no longer supported"; exit 1; )
BUILDER=catkin
ROSWS=wstool

trap error ERR

### before_install: # Use this to prepare the system to install prerequisites or dependencies
## to avoid stty error, until catkin_tools 2.0.x (http://stackoverflow.com/questions/27969057/cant-launch-catkin-build-from-jenkins-job)
sudo apt-get install -q -qq -y python-setuptools
[ ! -e /tmp/catkin_tools ] && (cd /tmp/; git clone -q https://github.com/catkin/catkin_tools)
(cd /tmp/catkin_tools; sudo python setup.py --quiet install)

# Define some config vars
export CI_SOURCE_PATH=$(pwd)
export REPOSITORY_NAME=${PWD##*/}
if [ ! "$ROS_PARALLEL_JOBS" ]; then export ROS_PARALLEL_JOBS="-j8 -l8";  fi
echo "Testing branch $TRAVIS_BRANCH of $REPOSITORY_NAME"
sudo sh -c 'echo "deb http://packages.ros.org/ros-shadow-fixed/ubuntu `lsb_release -cs` main" > /etc/apt/sources.list.d/ros-latest.list'
wget http://packages.ros.org/ros.key -O - | sudo apt-key add -
lsb_release -a
sudo apt-get update
sudo apt-get install -y -q -qq python-rosdep python-wstool python-catkin-tools ros-$ROS_DISTRO-rosbash
if [ "$EXTRA_DEB" ]; then sudo apt-get install -q -qq -y $EXTRA_DEB;  fi
# MongoDB hack - I don't fully understand this but its for moveit_warehouse
dpkg -s mongodb || echo "ok"; export HAVE_MONGO_DB=$?
if [ $HAVE_MONGO_DB == 0 ]; then sudo apt-get remove -q -qq -y mongodb mongodb-10gen || echo "ok"; fi
if [ $HAVE_MONGO_DB == 0 ]; then sudo apt-get install -q -qq -y mongodb-clients mongodb-server -o Dpkg::Options::="--force-confdef" || echo "ok"; fi # default actions
# Setup rosdep
sudo rosdep init
ret=1
rosdep update || while [ $ret != 0 ]; do sleep 1; rosdep update && ret=0 || echo "failed"; done

### install: # Use this to install any prerequisites or dependencies necessary to run your build
# Create workspace
mkdir -p ~/ros/ws_$REPOSITORY_NAME/src
cd ~/ros/ws_$REPOSITORY_NAME/src
if [ "$USE_DEB" == false ]; then $ROSWS init .   ; fi
if [ "$USE_DEB" == false ]; then $ROSWS merge file://$CI_SOURCE_PATH/.rosinstall      ; fi
if [ "$USE_DEB" == false ]; then sed -i "s@^\(.*github.com/$TRAVIS_REPO_SLUG.*\)@#\1@" .rosinstall               ; fi # comment out current repo
if [ "$USE_DEB" == false ]; then $ROSWS update   ; fi
if [ "$USE_DEB" == false ]; then $ROSWS set $REPOSITORY_NAME http://github.com/$TRAVIS_REPO_SLUG --git -y        ; fi
ln -s $CI_SOURCE_PATH . # Link the repo we are testing to the new workspace
if [ "$USE_DEB" == source -a -e $REPOSITORY_NAME/setup_upstream.sh ]; then $ROSWS init .; $REPOSITORY_NAME/setup_upstream.sh -w ~/ros/ws_$REPOSITORY_NAME ; $ROSWS update; fi
cd ../
# Install dependencies for source repos
if [ "$ROSDEP_UPDATE_QUIET" == "true" ]; then
    ROSDEP_ARGS=>/dev/null
fi
source /opt/ros/$ROS_DISTRO/setup.bash # ROS_PACKAGE_PATH is important for rosdep
if [ -e ${CI_SOURCE_PATH}/.travis/rosdep-install.sh ]; then ## this is mainly for jsk_travis itself
    ${CI_SOURCE_PATH}/.travis/rosdep-install.sh
else
    wget http://raw.github.com/jsk-ros-pkg/jsk_travis/master/rosdep-install.sh -O - | bash
fi


### before_script: # Use this to prepare your build for testing e.g. copy database configurations, environment variables, etc.
source /opt/ros/$ROS_DISTRO/setup.bash # re-source setup.bash for setting environmet vairable for package installed via rosdep

### script: # All commands must exit with code 0 on success. Anything else is considered failure.
# for catkin
if [ "$BUILDER" == catkin ]; then catkin build -i -v --no-status $BUILD_PKGS --make-args $ROS_PARALLEL_JOBS            ; fi
if [ "$BUILDER" == catkin ]; then catkin run_tests --no-status $BUILD_PKGS --make-args $ROS_PARALLEL_JOBS --           ; fi
if [ "$BUILDER" == catkin ]; then find build -name LastTest.log -exec echo "==== {} ====" \; -exec cat {} \;  ; fi
if [ "$NOT_TEST_INSTALL" != "true" ]; then
    if [ "$BUILDER" == catkin ]; then catkin clean -a                        ; fi
    if [ "$BUILDER" == catkin ]; then catkin config --install                ; fi
    if [ "$BUILDER" == catkin ]; then catkin build -i -v --no-status $BUILD_PKGS --make-args $ROS_PARALLEL_JOBS            ; fi
    if [ "$BUILDER" == catkin ]; then source install/setup.bash              ; fi
    if [ "$BUILDER" == catkin ]; then export EXIT_STATUS=0; for pkg in $TARGET_PKG; do [ "`find install/share/$pkg -iname '*.test'`" == "" ] && echo "[$pkg] No tests ware found!!!"  || find install/share/$pkg -iname "*.test" -print0 | xargs -0 -n1 rostest || export EXIT_STATUS=$?; done; [ $EXIT_STATUS == 0 ] ; fi
fi
