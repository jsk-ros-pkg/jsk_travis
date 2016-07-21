#!/bin/bash

set -x

function travis_time_start {
    set +x
    TRAVIS_START_TIME=$(date +%s%N)
    TRAVIS_TIME_ID=$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 8 | head -n 1)
    TRAVIS_FOLD_NAME=$1
    echo -e "\e[0Ktraivs_fold:start:$TRAVIS_FOLD_NAME"
    echo -e "\e[0Ktraivs_time:start:$TRAVIS_TIME_ID\e[34m>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\e[0m"
    set -x
}
function travis_time_end {
    set +x
    _COLOR=${1:-32}
    TRAVIS_END_TIME=$(date +%s%N)
    TIME_ELAPSED_SECONDS=$(( ($TRAVIS_END_TIME - $TRAVIS_START_TIME)/1000000000 ))
    echo -e "traivs_time:end:$TRAVIS_TIME_ID:start=$TRAVIS_START_TIME,finish=$TRAVIS_END_TIME,duration=$(($TRAVIS_END_TIME - $TRAVIS_START_TIME))\n\e[0K"
    echo -e "traivs_fold:end:$TRAVIS_FOLD_NAME\e[${_COLOR}m<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\e[0m"
    echo -e "\e[0K\e[${_COLOR}mFunction $TRAVIS_FOLD_NAME takes $(( $TIME_ELAPSED_SECONDS / 60 )) min $(( $TIME_ELAPSED_SECONDS % 60 )) sec\e[0m"
    set -x
}

# set default values to env variables
[ "${USE_TRAVIS// }" = "" ] && USE_TRAVIS=false

# Deprecated environmental variables
[ ! -z $BUILDER -a "$BUILDER" != catkin ] && ( echo "ERROR: $BUILDER is not supported. BUILDER env is deprecated and only 'catkin' is supported for the build."; exit 1; )
[ ! -z $ROSWS -a "$ROSWS" != wstool ] && ( echo "ERROR: $ROSWS is not supported. ROSWS env is deprecated and only 'wstool' is supported for workspace management."; exit 1; )

if [ "$USE_TRAVIS" != "true" ] && [ "$ROS_DISTRO" == "indigo" -o "$ROS_DISTRO" == "jade" -o "$ROS_DISTRO" == "kinetic" -o "${USE_JENKINS}" == "true" ] && [ "$TRAVIS_JOB_ID" ]; then
    pip install --user python-jenkins -q
    ./.travis/travis_jenkins.py
    exit $?
fi

function error {
    travis_time_end 31
    trap - ERR
    exit 1
}

trap error ERR

git branch --all
if [ "`git diff origin/master FETCH_HEAD .travis`" != "" ] ; then DIFF=`git diff origin/master FETCH_HEAD .travis | grep .*Subproject | sed s'@.*Subproject commit @@' | sed 'N;s/\n/.../'`; (cd .travis/;git log --oneline --graph --left-right --first-parent --decorate $DIFF) | tee /tmp/$$-travis-diff.log; grep -c '<' /tmp/$$-travis-diff.log && exit 1; echo "ok"; fi


travis_time_start setup_ros

# Define some config vars
export CI_SOURCE_PATH=$(pwd)
export REPOSITORY_NAME=${PWD##*/}
if [ ! "$ROS_PARALLEL_JOBS" ]; then export ROS_PARALLEL_JOBS="-j8";  fi
if [ ! "$CATKIN_PARALLEL_JOBS" ]; then export CATKIN_PARALLEL_JOBS="-p4";  fi
if [ ! "$ROS_PARALLEL_TEST_JOBS" ]; then export ROS_PARALLEL_TEST_JOBS="$ROS_PARALLEL_JOBS";  fi
if [ ! "$CATKIN_PARALLEL_TEST_JOBS" ]; then export CATKIN_PARALLEL_TEST_JOBS="$CATKIN_PARALLEL_JOBS";  fi
if [ ! "$ROS_REPOSITORY_PATH" ]; then export ROS_REPOSITORY_PATH="http://packages.ros.org/ros-shadow-fixed/ubuntu"; fi
if [ ! "$ROSDEP_ADDITIONAL_OPTIONS" ]; then export ROSDEP_ADDITIONAL_OPTIONS="-n -q -r --ignore-src"; fi
if [ ! "$CATKIN_TOOLS_BUILD_OPTIONS" ]; then export CATKIN_TOOLS_BUILD_OPTIONS="--summarize --no-status"; fi
echo "Testing branch $TRAVIS_BRANCH of $REPOSITORY_NAME"
# Setup pip
# FIXME: need to specify pip version to 6.0.7 to avoid unexpected error
# https://github.com/jsk-ros-pkg/jsk_robot/pull/523#issuecomment-164699366
sudo easy_install 'pip==6.0.7'
sudo pip install -U -q pip setuptools
# Setup apt
sudo -E sh -c 'echo "deb $ROS_REPOSITORY_PATH `lsb_release -cs` main" > /etc/apt/sources.list.d/ros-latest.list'
wget http://packages.ros.org/ros.key -O - | sudo apt-key add -
lsb_release -a
sudo apt-get update -q || echo Ignore error of apt-get update
sudo apt-get install -y --force-yes -q -qq python-rosdep python-wstool python-catkin-tools ros-$ROS_DISTRO-rosbash ros-$ROS_DISTRO-rospack ccache
# setup ccache
sudo ln -s /usr/bin/ccache /usr/local/bin/gcc
sudo ln -s /usr/bin/ccache /usr/local/bin/g++
sudo ln -s /usr/bin/ccache /usr/local/bin/cc
sudo ln -s /usr/bin/ccache /usr/local/bin/c++
ccache -s

if [ "$EXTRA_DEB" ]; then sudo apt-get install -q -qq -y $EXTRA_DEB;  fi
# MongoDB hack - I don't fully understand this but its for moveit_warehouse
dpkg -s mongodb || echo "ok"; export HAVE_MONGO_DB=$?
if [ $HAVE_MONGO_DB == 0 ]; then
    sudo apt-get remove --purge -q -qq -y mongodb mongodb-10gen || echo "ok"
    sudo apt-get install -y --force-yes -q -qq  mongodb-clients mongodb-server -o Dpkg::Options::="--force-confdef" || echo "ok"
fi # default actions

travis_time_end
travis_time_start setup_rosdep

# Setup rosdep
pip --version
rosdep --version
sudo rosdep init
ret=1
rosdep update || while [ $ret != 0 ]; do sleep 1; rosdep update && ret=0 || echo "failed"; done

travis_time_end
travis_time_start setup_catkin

### before_install: # Use this to prepare the system to install prerequisites or dependencies
### https://github.com/ros/catkin/pull/705
if [ "$ROS_DISTRO" == "hydro" ]; then
  [ ! -e /tmp/catkin ] && (cd /tmp/; git clone -q https://github.com/ros/catkin)
  (cd /tmp/catkin; git checkout 1b5f6fb2f0a3460c45885e26e7fa9ca1e52f1b87; cmake . -DCMAKE_INSTALL_PREFIX=/opt/ros/$ROS_DISTRO/ ; make; sudo make install)
else
  sudo apt-get install -y --force-yes -q -qq ros-$ROS_DISTRO-catkin
fi
sudo apt-get install -y --force-yes -q -qq ros-$ROS_DISTRO-roslaunch
### https://github.com/ros/ros_comm/pull/641
(cd /opt/ros/$ROS_DISTRO/lib/python2.7/dist-packages; wget --no-check-certificate https://patch-diff.githubusercontent.com/raw/ros/ros_comm/pull/641.diff -O /tmp/641.diff; [ "$ROS_DISTRO" == "hydro" ] && sed -i s@items@iteritems@ /tmp/641.diff ; sudo patch -p4 < /tmp/641.diff)


travis_time_end

# Check ROS tool's version
echo -e "\e[0KROS tool's version"
source /opt/ros/$ROS_DISTRO/setup.bash > /tmp/$$.x 2>&1; grep export\ [^_] /tmp/$$.x
rosversion roslaunch
rosversion rospack
apt-cache show python-rospkg | grep '^Version:' | awk '{print $2}'

travis_time_start setup_rosws

### install: # Use this to install any prerequisites or dependencies necessary to run your build
# Create workspace
mkdir -p ~/ros/ws_$REPOSITORY_NAME/src
cd ~/ros/ws_$REPOSITORY_NAME
catkin init
catkin config $CATKIN_TOOLS_CONFIG_OPTIONS
cd ~/ros/ws_$REPOSITORY_NAME/src
if [ "$USE_DEB" == false ]; then
    wstool init .
    if [ -e $CI_SOURCE_PATH/.travis.rosinstall ]; then
        # install (maybe unreleased version) dependencies from source
        wstool merge file://$CI_SOURCE_PATH/.travis.rosinstall
    fi
    if [ -e $CI_SOURCE_PATH/.travis.rosinstall.$ROS_DISTRO ]; then
        # install (maybe unreleased version) dependencies from source for specific ros version
        wstool merge file://$CI_SOURCE_PATH/.travis.rosinstall.$ROS_DISTRO
    fi
    wstool update
fi
ln -s $CI_SOURCE_PATH . # Link the repo we are testing to the new workspace
if [ "$USE_DEB" == source -a -e $REPOSITORY_NAME/setup_upstream.sh ]; then wstool init .; $REPOSITORY_NAME/setup_upstream.sh -w ~/ros/ws_$REPOSITORY_NAME ; wstool update; fi
# disable hrpsys/doc generation
find . -ipath "*/hrpsys/CMakeLists.txt" -exec sed -i s'@if(ENABLE_DOXYGEN)@if(0)@' {} \;
# disable metapackage
find -L . -name package.xml -print -exec ${CI_SOURCE_PATH}/.travis/check_metapackage.py {} \; -a -exec bash -c 'touch `dirname ${1}`/CATKIN_IGNORE' funcname {} \;

# Install dependencies for source repos
if [ "$ROSDEP_UPDATE_QUIET" == "true" ]; then
    ROSDEP_ARGS=>/dev/null
fi
source /opt/ros/$ROS_DISTRO/setup.bash > /tmp/$$.x 2>&1; grep export\ [^_] /tmp/$$.x # ROS_PACKAGE_PATH is important for rosdep

if [ ! -e .rosinstall ]; then
    echo "- git: {local-name: $REPOSITORY_NAME, uri: 'http://github.com/$TRAVIS_REPO_SLUG'}" >> .rosinstall
fi

travis_time_end

travis_time_start before_script

### before_script: # Use this to prepare your build for testing e.g. copy database configurations, environment variables, etc.
source /opt/ros/$ROS_DISTRO/setup.bash > /tmp/$$.x 2>&1; grep export\ [^_] /tmp/$$.x # re-source setup.bash for setting environmet vairable for package installed via rosdep
if [ "${BEFORE_SCRIPT// }" != "" ]; then sh -c "${BEFORE_SCRIPT}"; fi

travis_time_end

travis_time_start rosdep_install

if [ -e ${CI_SOURCE_PATH}/.travis/rosdep-install.sh ]; then ## this is mainly for jsk_travis itself
    ${CI_SOURCE_PATH}/.travis/rosdep-install.sh
else
    wget http://raw.github.com/jsk-ros-pkg/jsk_travis/master/rosdep-install.sh -O - | bash
fi


travis_time_end

wstool --version
wstool info -t .
cd ../

travis_time_start catkin_build

### script: # All commands must exit with code 0 on success. Anything else is considered failure.
source /opt/ros/$ROS_DISTRO/setup.bash > /tmp/$$.x 2>&1; grep export\ [^_] /tmp/$$.x # re-source setup.bash for setting environmet vairable for package installed via rosdep
# for catkin
if [ "${TARGET_PKGS// }" == "" ]; then export TARGET_PKGS=`catkin_topological_order ${CI_SOURCE_PATH} --only-names`; fi
if [ "${TEST_PKGS// }" == "" ]; then export TEST_PKGS=$( [ "${BUILD_PKGS// }" == "" ] && echo "$TARGET_PKGS" || echo "$BUILD_PKGS"); fi
set -o pipefail  # this is necessary to pipe fail status on grepping
catkin build $CATKIN_TOOLS_BUILD_OPTIONS $BUILD_PKGS $CATKIN_PARALLEL_JOBS --make-args $ROS_PARALLEL_JOBS | grep -v -e Symlinking -e Linked
set +o pipefail

travis_time_end
travis_time_start catkin_run_tests

# patch for rostest
(cd /opt/ros/$ROS_DISTRO/lib/python2.7/dist-packages; wget --no-check-certificate https://patch-diff.githubusercontent.com/raw/ros/ros_comm/pull/611.diff -O - | sudo patch -f -p4 || echo "ok" )
if [ "$ROS_DISTRO" == "hydro" ]; then
    (cd /opt/ros/$ROS_DISTRO/lib/python2.7/dist-packages; wget --no-check-certificate https://patch-diff.githubusercontent.com/raw/ros/ros/pull/82.diff -O - | sudo patch -p4)
    (cd /opt/ros/$ROS_DISTRO/share; wget --no-check-certificate https://patch-diff.githubusercontent.com/raw/ros/ros_comm/pull/611.diff -O - | sed s@.cmake.em@.cmake@ | sed 's@/${PROJECT_NAME}@@' | sed 's@ DEPENDENCIES ${_rostest_DEPENDENCIES})@)@' | sudo patch -f -p2 || echo "ok")
fi

source devel/setup.bash > /tmp/$$.x 2>&1; grep export\ [^_] /tmp/$$.x ; rospack profile # force to update ROS_PACKAGE_PATH for rostest
set -o pipefail  # this is necessary to pipe fail status on grepping
catkin run_tests -i --no-deps --no-status $TEST_PKGS $CATKIN_PARALLEL_TEST_JOBS --make-args $ROS_PARALLEL_TEST_JOBS -- | grep -v -e Symlinking -e Linked -e :[^\s]*install[^\s]*\]
set +o pipefail
catkin_test_results --verbose --all build || error

travis_time_end

if [ "$NOT_TEST_INSTALL" != "true" ]; then

    travis_time_start catkin_install_build

    catkin clean --yes || catkin clean -a # 0.3.1 uses -a, 0.4.0 uses --yes
    catkin config --install $CATKIN_TOOLS_CONFIG_OPTIONS
    set -o pipefail  # this is necessary to pipe fail status on grepping
    catkin build $CATKIN_TOOLS_BUILD_OPTIONS $BUILD_PKGS $CATKIN_PARALLEL_JOBS --make-args $ROS_PARALLEL_JOBS | grep -v -e Symlinking -e Linked -e :[^\s]*install[^\s]*\]
    set +o pipefail
    source install/setup.bash > /tmp/$$.x 2>&1; grep export\ [^_] /tmp/$$.x
    rospack profile
    rospack plugins --attrib=plugin nodelet || echo "ok"

    travis_time_end
    travis_time_start catkin_install_run_tests

    export EXIT_STATUS=0
    for pkg in $TEST_PKGS; do
      echo "[$pkg] Started testing..."
      rostest_files=$(find install/share/$pkg -iname '*.test')
      echo "[$pkg] Found $(echo $rostest_files | wc -w) tests."
      for test_file in $rostest_files; do
        echo "[$pkg] Testing $test_file"
        rostest $test_file || export EXIT_STATUS=$?
        if [ $? != 0 ]; then
          echo -e "[$pkg] Testing again the failed test: $test_file.\e[31m>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\e[0m"
          rostest --text $test_file
          echo -e "[$pkg] Testing again the failed test: $test_file.\e[31m<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\e[0m"
        fi
      done
    done
    [ $EXIT_STATUS -eq 0 ] || error  # unless all tests pass, raise error

    travis_time_end

fi

travis_time_start after_script

## after_script
PATH=/usr/local/bin:$PATH  # for installed catkin_test_results
PYTHONPATH=/usr/local/lib/python2.7/dist-packages:$PYTHONPATH
if [ "${ROS_LOG_DIR// }" == "" ]; then export ROS_LOG_DIR=~/.ros/test_results; fi # http://wiki.ros.org/ROS/EnvironmentVariables#ROS_LOG_DIR
if [ -e $ROS_LOG_DIR ]; then catkin_test_results --verbose --all $ROS_LOG_DIR || error; fi
if [ -e ~/ros/ws_$REPOSITORY_NAME/build/ ]; then catkin_test_results --verbose --all ~/ros/ws_$REPOSITORY_NAME/build/ || error; fi
if [ -e ~/.ros/test_results/ ]; then catkin_test_results --verbose --all ~/.ros/test_results/ || error; fi

travis_time_end
