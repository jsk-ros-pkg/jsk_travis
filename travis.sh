#!/bin/bash

set -x

function travis_time_start {
    set +x
    TRAVIS_START_TIME=$(date +%s%N)
    TRAVIS_TIME_ID=$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 8 | head -n 1)
    TRAVIS_FOLD_NAME=$1
    echo -e "${ANSI_CLEAR}traivs_fold:start:$TRAVIS_FOLD_NAME"
    echo -e "${ANSI_CLEAR}traivs_time:start:$TRAVIS_TIME_ID${ANSI_BLUE}>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>${ANSI_RESET}"
    set -x
}
function travis_time_end {
    set +x
    _COLOR=${1:-32}
    TRAVIS_END_TIME=$(date +%s%N)
    TIME_ELAPSED_SECONDS=$(( ($TRAVIS_END_TIME - $TRAVIS_START_TIME)/1000000000 ))
    echo -e "traivs_time:end:$TRAVIS_TIME_ID:start=$TRAVIS_START_TIME,finish=$TRAVIS_END_TIME,duration=$(($TRAVIS_END_TIME - $TRAVIS_START_TIME))\n${ANSI_CLEAR}"
    echo -e "traivs_fold:end:$TRAVIS_FOLD_NAME\e[${_COLOR}m<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<${ANSI_RESET}"
    echo -e "${ANSI_CLEAR}\e[${_COLOR}mFunction $TRAVIS_FOLD_NAME takes $(( $TIME_ELAPSED_SECONDS / 60 )) min $(( $TIME_ELAPSED_SECONDS % 60 )) sec${ANSI_RESET}"
    set -x
}


echo "Running jsk_travis/travis.sh whose version is $(cd .travis && git describe --all)."

travis_time_start setup_variables

export CI_SOURCE_PATH=$(pwd)
export REPOSITORY_NAME=${PWD##*/}

ANSI_RED="\033[31;1m"
ANSI_GREEN="\033[32;1m"
ANSI_BLUE="\033[34;1m"
ANSI_RESET="\033[0m"
ANSI_CLEAR="\033[0K"

travis_time_end
travis_time_start is_jsk_travis_upgraded

# Check if jsk_travis is upgraded, because downgrading jsk_travis is not supported.
if [ "$(git diff origin/master HEAD $CI_SOURCE_PATH/.travis)" != "" ] ; then
  # HASH_TO_HASH represents: "jsk_travis version commited to origin/master" .. "jsk_travis to be commited with this PR"
  # ex. 5f047fd5a8c0714c091b965b80b1f3719697c36a...0417ddc12c0b8ca4d10a86844745dd1279534845
  HASH_TO_HASH=$(git diff origin/master HEAD $CI_SOURCE_PATH/.travis | grep .*Subproject | sed s'@.*Subproject commit @@' | sed 'N;s/\n/.../')
  COMMITS=$(cd $CI_SOURCE_PATH/.travis/; git log --oneline --graph --left-right --first-parent --decorate $HASH_TO_HASH)
  if [ $(echo "$COMMITS" | grep -c '^<' ) -eq 0 ]; then
    echo INFO: jsk_travis is successfully upgraded comparing the version commited to origin/master.
    echo It is $(echo "$COMMITS" | grep -c '^>') commits ahead.
  else
    echo ERROR: jsk_travis is downgraded comparing the version commited to origin/master, and this is not supported.
    echo It is $(echo "$COMMITS" | grep -c '^<') commits behind, and the commits are below:
    echo "$COMMITS" | grep -c '^<'
    error
  fi
fi

travis_time_end


# set default values to env variables
[ "${USE_TRAVIS// }" = "" ] && USE_TRAVIS=false

# Deprecated environmental variables
[ ! -z $BUILDER ] && [ "$BUILDER" != catkin ] && ( echo "ERROR: $BUILDER is not supported. BUILDER env is deprecated and only 'catkin' is supported for the build."; exit 1; )
[ ! -z $ROSWS ] && [ "$ROSWS" != wstool ] && ( echo "ERROR: $ROSWS is not supported. ROSWS env is deprecated and only 'wstool' is supported for workspace management."; exit 1; )

# docker on travis
if [ "$USE_DOCKER" = true ]; then
  if [ "$DOCKER_IMAGE" = "" ]; then
    case $ROS_DISTRO in
      hydro) DISTRO=precise;;
      indigo|jade) DISTRO=trusty;;
      kinetic|lunar) DISTRO=xenial;;
      melodic) DISTRO=bionic;;
      *) DISTRO=trusty;;
    esac
    export DOCKER_IMAGE=ubuntu:$DISTRO
  fi

  travis_time_start setup_apt_cacher_ng

  # start apt-cacher-ng
  sudo apt-get update && sudo apt-get install -y apt-cacher-ng
  sudo sed -i "s@CacheDir: /var/cache/apt-cacher-ng@CacheDir: $HOME/apt-cacher-ng@" /etc/apt-cacher-ng/acng.conf
  grep CacheDir /etc/apt-cacher-ng/acng.conf
  sudo chmod 777 $HOME/apt-cacher-ng && sudo /etc/init.d/apt-cacher-ng restart
  ls -al /var/cache/apt-cacher-ng
  ls -al /var/cache/apt-cacher-ng/
  ls -al $HOME/apt-cacher-ng
  ls -al $HOME/apt-cacher-ng/
  sudo tail -n 100 /var/log/apt-cacher-ng/*

  travis_time_end

  DOCKER_XSERVER_OPTIONS=''
  if [ "$TRAVIS_SUDO" = true ]; then

    travis_time_start setup_docker_x11

    # use host xserver
    sudo apt-get update -q || echo Ignore error of apt-get update
    sudo apt-get -y -qq install mesa-utils x11-xserver-utils xserver-xorg-video-dummy
    export DISPLAY=:0
    sudo Xorg -noreset +extension GLX +extension RANDR +extension RENDER -logfile /tmp/xorg.log -config $CI_SOURCE_PATH/.travis/dummy.xorg.conf $DISPLAY &
    sleep 3 # wait x server up
    glxinfo | grep GLX
    export QT_X11_NO_MITSHM=1 # http://wiki.ros.org/docker/Tutorials/GUI
    xhost +local:root
    DOCKER_XSERVER_OPTIONS='-v /tmp/.X11-unix:/tmp/.X11-unix -e QT_X11_NO_MITSHM -e DISPLAY'

    travis_time_end

  fi

  docker pull $DOCKER_IMAGE || true
  docker run -v $HOME:$HOME -v $HOME/.ccache:$HOME/.ccache/ -v $HOME/.cache/pip:$HOME/.cache/pip/ \
    $DOCKER_XSERVER_OPTIONS \
    -e TRAVIS_BRANCH -e TRAVIS_COMMIT -e TRAVIS_JOB_ID -e TRAVIS_OS_NAME -e TRAVIS_PULL_REQUEST -e TRAVIS_REPO_SLUG \
    -e CI_SOURCE_PATH -e HOME -e REPOSITORY_NAME \
    -e BUILD_PKGS -e TARGET_PKGS -e TEST_PKGS \
    -e BEFORE_SCRIPT -e BUILDER -e EXTRA_DEB -e USE_DEB \
    -e ROS_DISTRO -e ROS_LOG_DIR -e ROS_REPOSITORY_PATH -e ROSWS \
    -e CATKIN_TOOLS_BUILD_OPTIONS -e CATKIN_TOOLS_CONFIG_OPTIONS \
    -e CATKIN_PARALLEL_JOBS -e CATKIN_PARALLEL_TEST_JOBS \
    -e ROS_PARALLEL_JOBS -e ROS_PARALLEL_TEST_JOBS \
    -e ROSDEP_ADDITIONAL_OPTIONS -e ROSDEP_UPDATE_QUIET \
    -e SUDO_PIP -e USE_PYTHON_VIRTUALENV \
    -e NOT_TEST_INSTALL \
    -t $DOCKER_IMAGE bash -c 'cd $CI_SOURCE_PATH; .travis/docker.sh'
  DOCKER_EXIT_CODE=$?
  sudo chown -R travis.travis $HOME/apt-cacher-ng
  sudo tail -n 100 /var/log/apt-cacher-ng/*
  sudo find $HOME/apt-cacher-ng
  sudo find /var/cache/apt-cacher-ng
  exit $DOCKER_EXIT_CODE
fi

if [ "$USE_TRAVIS" != "true" ] && [ "$ROS_DISTRO" != "hydro" -o "${USE_JENKINS}" == "true" ] && [ "$TRAVIS_JOB_ID" ]; then
    pip install --user -U python-jenkins==1.4.0 -q
    ./.travis/travis_jenkins.py
    exit $?
fi

function error {
    travis_time_end 31
    trap - ERR
    exit 1
}

trap error ERR


travis_time_start setup_ros

# Define some config vars
export CI_SOURCE_PATH=$(pwd)
export REPOSITORY_NAME=${PWD##*/}
if [ ! "$ROS_PARALLEL_JOBS" ]; then export ROS_PARALLEL_JOBS="-j8";  fi
if [ ! "$CATKIN_PARALLEL_JOBS" ]; then export CATKIN_PARALLEL_JOBS="-p4";  fi
if [ ! "$ROS_PARALLEL_TEST_JOBS" ]; then export ROS_PARALLEL_TEST_JOBS="$ROS_PARALLEL_JOBS";  fi
if [ ! "$CATKIN_PARALLEL_TEST_JOBS" ]; then export CATKIN_PARALLEL_TEST_JOBS="$CATKIN_PARALLEL_JOBS";  fi
if [ ! "$ROS_REPOSITORY_PATH" ]; then export ROS_REPOSITORY_PATH="http://packages.ros.org/ros-testing/ubuntu"; fi
if [ ! "$ROSDEP_ADDITIONAL_OPTIONS" ]; then export ROSDEP_ADDITIONAL_OPTIONS="-n -q -r --ignore-src"; fi
echo "Testing branch $TRAVIS_BRANCH of $REPOSITORY_NAME"

# Install pip
curl https://bootstrap.pypa.io/get-pip.py | sudo python -
# pip>=10 no longer uninstalls distutils packages (ex. packages installed via apt),
# and fails to install packages via pip if they are already installed via apt.
# See https://github.com/pypa/pip/issues/4805 for detail.
sudo -H pip install 'pip<10'

# set DEBIAN_FRONTEND=noninteractive
echo 'debconf debconf/frontend select Noninteractive' | sudo debconf-set-selections
# Setup apt
sudo -E sh -c 'echo "deb $ROS_REPOSITORY_PATH `lsb_release -cs` main" > /etc/apt/sources.list.d/ros-latest.list'
wget http://packages.ros.org/ros.key -O - | sudo apt-key add -
lsb_release -a
# Setup EoL repository
if [[ "$ROS_DISTRO" ==  "hydro" || "$ROS_DISTRO" ==  "jade" || "$ROS_DISTRO" ==  "lunar" ]]; then
    sudo -E sh -c 'echo "deb http://snapshots.ros.org/$ROS_DISTRO/final/ubuntu `lsb_release -sc` main" >> /etc/apt/sources.list.d/ros-latest.list'
    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key 0xCBF125EA
fi
# Install base system
sudo apt-get update -q || echo Ignore error of apt-get update
sudo apt-get install -y --force-yes -q -qq dpkg # https://github.com/travis-ci/travis-ci/issues/9361#issuecomment-408431262 dpkg-deb: error: archive has premature member 'control.tar.xz' before 'control.tar.gz' #9361
sudo apt-get install -y --force-yes -q -qq python-rosdep python-wstool python-catkin-tools ros-$ROS_DISTRO-rosbash ros-$ROS_DISTRO-rospack ccache pv
# setup catkin-tools option
if [ ! "$CATKIN_TOOLS_BUILD_OPTIONS" ]; then
  if [[ "$(pip show catkin-tools | grep '^Version:' | awk '{print $2}')" =~ 0.3.[0-9]+ ]]; then
    # For catkin-tools==0.3.X, '-iv' option is required to get the stderr output.
    export CATKIN_TOOLS_BUILD_OPTIONS="-iv --summarize --no-status"
  else
    export CATKIN_TOOLS_BUILD_OPTIONS="--summarize --no-status"
  fi
fi
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
if [ ! -e /etc/ros/rosdep/sources.list.d/20-default.list ]; then
    sudo rosdep init
fi
ret=1
rosdep update --include-eol-distros|| while [ $ret != 0 ]; do sleep 1; rosdep update --include-eol-distros && ret=0 || echo "failed"; done

travis_time_end
travis_time_start setup_catkin

### before_install: # Use this to prepare the system to install prerequisites or dependencies
if [ "$ROS_DISTRO" == "hydro" ]; then
  [ ! -e /tmp/catkin ] && (cd /tmp/; git clone -q https://github.com/ros/catkin)
  (cd /tmp/catkin; git checkout 0.6.12; cmake . -DCMAKE_INSTALL_PREFIX=/opt/ros/$ROS_DISTRO/ ; make; sudo make install)
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
wstool init
if [ "$USE_DEB" == false ]; then
    if [ -e $CI_SOURCE_PATH/.travis.rosinstall ]; then
        # install (maybe unreleased version) dependencies from source
        wstool merge file://$CI_SOURCE_PATH/.travis.rosinstall
    fi
    if [ -e $CI_SOURCE_PATH/.travis.rosinstall.$ROS_DISTRO ]; then
        # install (maybe unreleased version) dependencies from source for specific ros version
        wstool merge --merge-replace -y file://$CI_SOURCE_PATH/.travis.rosinstall.$ROS_DISTRO
    fi
    wstool update
fi
ln -s $CI_SOURCE_PATH . # Link the repo we are testing to the new workspace
if [ "$USE_DEB" == source -a -e $REPOSITORY_NAME/setup_upstream.sh ]; then $REPOSITORY_NAME/setup_upstream.sh -w ~/ros/ws_$REPOSITORY_NAME ; wstool update; fi
# disable hrpsys/doc generation
find . -ipath "*/hrpsys/CMakeLists.txt" -exec sed -i s'@if(ENABLE_DOXYGEN)@if(0)@' {} \;
# disable metapackage
find -L . -name package.xml -print -exec ${CI_SOURCE_PATH}/.travis/check_metapackage.py {} \; -a -exec bash -c 'touch `dirname ${1}`/CATKIN_IGNORE' funcname {} \;

# Install dependencies for source repos
if [ "$ROSDEP_UPDATE_QUIET" == "true" ]; then
    ROSDEP_ARGS=>/dev/null
fi
source /opt/ros/$ROS_DISTRO/setup.bash > /tmp/$$.x 2>&1; grep export\ [^_] /tmp/$$.x # ROS_PACKAGE_PATH is important for rosdep

travis_time_end

travis_time_start before_script

### before_script: # Use this to prepare your build for testing e.g. copy database configurations, environment variables, etc.
source /opt/ros/$ROS_DISTRO/setup.bash > /tmp/$$.x 2>&1; grep export\ [^_] /tmp/$$.x # re-source setup.bash for setting environmet vairable for package installed via rosdep
if [ "${BEFORE_SCRIPT// }" != "" ]; then sh -c "${BEFORE_SCRIPT}"; fi

travis_time_end

travis_time_start setup_pip_cache

# setup pip cache
# Store docker cache
if [ `whoami` = travis ]; then
   sudo rm -fr /root/.cache/pip
   sudo cp -r $HOME/.cache/pip /root/.cache/
   sudo chown -R root:root /root/.cache/pip/
fi
# Show cached PIP packages
sudo find -L $HOME/.cache/ | grep whl || echo "OK"
sudo find -L /root/.cache/ | grep whl || echo "OK"

travis_time_end

travis_time_start rosdep_install

if [ -e ${CI_SOURCE_PATH}/.travis/rosdep-install.sh ]; then ## this is mainly for jsk_travis itself
    ${CI_SOURCE_PATH}/.travis/rosdep-install.sh
else
    wget http://raw.github.com/jsk-ros-pkg/jsk_travis/master/rosdep-install.sh -O - | bash
fi

# Store docker cache
if [ `whoami` = travis ]; then
    sudo rm -fr $HOME/.cache/pip/*
    sudo cp -r /root/.cache/pip/ $HOME/.cache/
    sudo chown -R travis.travis $HOME/.cache/pip/*
fi
# Show cached PIP packages
sudo find -L /root/.cache/ | grep whl || echo "OK"
sudo find -L $HOME/.cache/ | grep whl || echo "OK"

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
if [ -z $TRAVIS_JOB_ID ]; then
  # on Jenkins
  catkin build $CATKIN_TOOLS_BUILD_OPTIONS $BUILD_PKGS $CATKIN_PARALLEL_JOBS --make-args $ROS_PARALLEL_JOBS --
else
  # on Travis, the command must outputs log within 10 min to avoid failures, so the `travis_wait` is necessary.
  travis_wait 60 catkin build $CATKIN_TOOLS_BUILD_OPTIONS $BUILD_PKGS $CATKIN_PARALLEL_JOBS --make-args $ROS_PARALLEL_JOBS --
fi

travis_time_end
travis_time_start catkin_run_tests

# patch for rostest
(cd /opt/ros/$ROS_DISTRO/lib/python2.7/dist-packages; wget --no-check-certificate https://patch-diff.githubusercontent.com/raw/ros/ros_comm/pull/611.diff -O - | sudo patch -f -p4 || echo "ok" )
if [ "$ROS_DISTRO" == "hydro" ]; then
    (cd /opt/ros/$ROS_DISTRO/lib/python2.7/dist-packages; wget --no-check-certificate https://patch-diff.githubusercontent.com/raw/ros/ros/pull/82.diff -O - | sudo patch -p4)
    (cd /opt/ros/$ROS_DISTRO/share; wget --no-check-certificate https://patch-diff.githubusercontent.com/raw/ros/ros_comm/pull/611.diff -O - | sed s@.cmake.em@.cmake@ | sed 's@/${PROJECT_NAME}@@' | sed 's@ DEPENDENCIES ${_rostest_DEPENDENCIES})@)@' | sudo patch -f -p2 || echo "ok")
fi

source devel/setup.bash > /tmp/$$.x 2>&1; grep export\ [^_] /tmp/$$.x ; rospack profile # force to update ROS_PACKAGE_PATH for rostest
# set -Werror=dev for developer errors (supported only fo kinetic and above)
if [[ "$ROS_DISTRO" > "indigo" ]] && [[ "$CMAKE_DEVELOPER_ERROR" == "true" ]]; then
  CMAKE_ARGS_FLAGS="--cmake-args -Werror=dev"
else
  CMAKE_ARGS_FLAGS=""
fi
if [ -z $TRAVIS_JOB_ID ]; then
  # on Jenkins
  catkin run_tests -i --no-deps --no-status $TEST_PKGS $CATKIN_PARALLEL_TEST_JOBS --make-args $ROS_PARALLEL_TEST_JOBS $CMAKE_ARGS_FLAGS --
else
  # on Travis
  travis_wait 60 catkin run_tests -i --no-deps --no-status $TEST_PKGS $CATKIN_PARALLEL_TEST_JOBS --make-args $ROS_PARALLEL_TEST_JOBS $CMAKE_ARGS_FLAGS --
fi
catkin_test_results --verbose --all build || error

travis_time_end

if [ "$NOT_TEST_INSTALL" != "true" ]; then

    travis_time_start catkin_install_build

    catkin clean --yes || catkin clean -a # 0.3.1 uses -a, 0.4.0 uses --yes
    catkin config --install $CATKIN_TOOLS_CONFIG_OPTIONS
    if [ -z $TRAVIS_JOB_ID ]; then
      # on Jenkins
      catkin build $CATKIN_TOOLS_BUILD_OPTIONS $BUILD_PKGS $CATKIN_PARALLEL_JOBS --make-args $ROS_PARALLEL_JOBS --
    else
      # on Travis
      travis_wait 60 catkin build $CATKIN_TOOLS_BUILD_OPTIONS $BUILD_PKGS $CATKIN_PARALLEL_JOBS --make-args $ROS_PARALLEL_JOBS --
    fi
    source install/setup.bash > /tmp/$$.x 2>&1; grep export\ [^_] /tmp/$$.x
    rospack profile
    rospack plugins --attrib=plugin nodelet || echo "ok"

    travis_time_end
    travis_time_start catkin_install_run_tests

    export EXIT_STATUS=0
    for pkg in $TEST_PKGS; do
      echo "[$pkg] Started testing..."
      rostest_files=$(test ! -d install/share/$pkg  || find install/share/$pkg -iname '*.test')
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
