#!/usr/bin/env python

from __future__ import print_function
# need pip installed version of python-jenkins > 0.4.0

import jenkins
import requests
import urllib
try:
    import urllib2
except:
    import urllib.request, urllib.error
import json
import time
import os
import re
import sys
import random
import string

from os import environ as env

CONFIGURE_XML = '''<?xml version='1.0' encoding='UTF-8'?>
<project>
  <actions/>
  <description>
     &lt;h4&gt;
     This is jenkins buildfirm for &lt;a href=http://github.com/%(TRAVIS_REPO_SLUG)s&gt;http://github.com/%(TRAVIS_REPO_SLUG)s&lt;/a&gt;&lt;br/&gt;
     see &lt;a href=http://travis-ci.org/%(TRAVIS_REPO_SLUG)s&gt;http://travis-ci.org/%(TRAVIS_REPO_SLUG)s&lt;/a&gt; for travis page that execute this job.&lt;br&gt;
     &lt;/h4&gt;
  </description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <jenkins.model.BuildDiscarderProperty>
      <strategy class="hudson.tasks.LogRotator">
        <daysToKeep>3</daysToKeep>
        <numToKeep>%(NUMBER_OF_LOGS_TO_KEEP)s</numToKeep>
        <artifactDaysToKeep>-1</artifactDaysToKeep>
        <artifactNumToKeep>-1</artifactNumToKeep>
      </strategy>
    </jenkins.model.BuildDiscarderProperty>
    <hudson.model.ParametersDefinitionProperty>
      <parameterDefinitions>
        <hudson.model.TextParameterDefinition>
          <name>TRAVIS_BRANCH</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>TRAVIS_COMMIT</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>TRAVIS_PULL_REQUEST</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>TRAVIS_REPO_SLUG</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>TRAVIS_BUILD_ID</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>TRAVIS_BUILD_NUMBER</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>TRAVIS_JOB_ID</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>TRAVIS_JOB_NUMBER</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>TRAVIS_JENKINS_UNIQUE_ID</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>ROS_DISTRO</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>USE_DEB</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>EXTRA_DEB</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>TEST_PKGS</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>TARGET_PKGS</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>BEFORE_SCRIPT</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>NOT_TEST_INSTALL</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>ROS_PARALLEL_JOBS</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>ROS_PYTHON_VERSION</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>CATKIN_PARALLEL_JOBS</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>CATKIN_TOOLS_BUILD_OPTIONS</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>CATKIN_TOOLS_CONFIG_OPTIONS</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>ROS_PARALLEL_TEST_JOBS</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>CATKIN_PARALLEL_TEST_JOBS</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>CMAKE_DEVELOPER_ERROR</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>BUILD_PKGS</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>ROS_REPOSITORY_PATH</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>ROSDEP_ADDITIONAL_OPTIONS</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>DOCKER_CONTAINER_NAME</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>DOCKER_RUN_OPTION</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>NUMBER_OF_LOGS_TO_KEEP</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>REPOSITORY_NAME</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>TRAVIS_BUILD_WEB_URL</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>TRAVIS_JOB_WEB_URL</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>DOCKER_IMAGE_JENKINS</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>TIMEOUT_JENKINS</name>
          <description></description>
          <defaultValue>120</defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>ADD_ENV_VALUE_TO_DOCKER</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
      </parameterDefinitions>
    </hudson.model.ParametersDefinitionProperty>
  </properties>
  <scm class='hudson.scm.NullSCM'/>
  <assignedNode>master</assignedNode>
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers/>
  <concurrentBuild>true</concurrentBuild>
  <builders>
    <hudson.tasks.Shell>
      <command>
function travis_time_start {
    set +x
    TRAVIS_START_TIME=$(date +%%s%%N)
    TRAVIS_TIME_ID=$RANDOM
    TRAVIS_FOLD_NAME=$1
    echo -e "${ANSI_CLEAR}traivs_fold:start:${TRAVIS_FOLD_NAME}"
    echo -e "${ANSI_CLEAR}traivs_time:start:${TRAVIS_TIME_ID}${ANSI_BLUE}&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;&gt;${ANSI_RESET}"
    set -x
}
function travis_time_end {
    set +x
    _COLOR=${1:-32}
    TRAVIS_END_TIME=$(date +%%s%%N)
    TIME_ELAPSED_SECONDS=$(( (${TRAVIS_END_TIME} - ${TRAVIS_START_TIME})/1000000000 ))
    echo -e "traivs_time:end:${TRAVIS_TIME_ID}:start=${TRAVIS_START_TIME},finish=${TRAVIS_END_TIME},duration=$((${TRAVIS_END_TIME} - ${TRAVIS_START_TIME}))\n${ANSI_CLEAR}"
    echo -e "traivs_fold:end:${TRAVIS_FOLD_NAME}\e[${_COLOR}m&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;${ANSI_RESET}"
    echo -e "${ANSI_CLEAR}\e[${_COLOR}mFunction ${TRAVIS_FOLD_NAME} takes $(( ${TIME_ELAPSED_SECONDS} / 60 )) min $(( ${TIME_ELAPSED_SECONDS} %% 60 )) sec${ANSI_RESET}"
}

travis_time_start setup_jenkins

set -x
set -e
env
WORKSPACE=`pwd`
[ "${BUILD_TAG}" = "" ] &amp;&amp; BUILD_TAG="build_tag" # jenkins usually has build_tag environment, note this is sh
trap "set +x" EXIT

# try git clone until success
until git clone https://github.com/$TRAVIS_REPO_SLUG ${BUILD_TAG}/$TRAVIS_REPO_SLUG
do
  echo "Retrying"
done
cd ${BUILD_TAG}/$TRAVIS_REPO_SLUG
#git fetch -q origin '+refs/pull/*:refs/remotes/pull/*'
#git checkout -qf $TRAVIS_COMMIT || git checkout -qf pull/${TRAVIS_PULL_REQUEST}/head
if [ "${TRAVIS_PULL_REQUEST}" != "false" ]; then
 git fetch -q origin +refs/pull/${TRAVIS_PULL_REQUEST}/merge
 git checkout -qf FETCH_HEAD
else
 git checkout -qf ${TRAVIS_COMMIT}
fi

git submodule init
git submodule update

if [ "$REPOSITORY_NAME" = "jsk_travis" ]; then
  mkdir .travis; cp -r * .travis # need to copy, since directory starting from . is ignoreed by catkin build
fi

travis_time_end
# travis_time_start docker_build

# # run docker build
# docker build -t $DOCKER_IMAGE_JENKINS -f $(echo .travis/docker/Dockerfile.$DOCKER_IMAGE_JENKINS | sed -e s/-[^-]*\$//) .travis/docker
# docker build -t $DOCKER_IMAGE_JENKINS --build-arg CACHEBUST=$(date +%%Y%%m%%d) -f .travis/docker/Dockerfile.$DOCKER_IMAGE_JENKINS .travis/docker

# travis_time_end
set +x

echo "DOCKER_CONTAINER_NAME: $DOCKER_CONTAINER_NAME"
echo "TRAVIS_BRANCH        : $TRAVIS_BRANCH"
echo "TRAVIS_COMMIT        : $TRAVIS_COMMIT"
echo "TRAVIS_PULL_REQUEST  : $TRAVIS_PULL_REQUEST"
echo "TRAVIS_REPO_SLUG     : $TRAVIS_REPO_SLUG"
echo "TRAVIS_BUILD_ID      : $TRAVIS_BUILD_ID"
echo "TRAVIS_BUILD_NUMBER  : $TRAVIS_BUILD_NUMBER"
echo "TRAVIS_JOB_ID        : $TRAVIS_JOB_ID"
echo "TRAVIS_JOB_NUMBER    : $TRAVIS_JOB_NUMBER"
echo "TRAVIS_JENKINS_UNIQUE_ID : $TRAVIS_JENKINS_UNIQUE_ID"
echo "ROS_DISTRO           : $ROS_DISTRO"
echo "USE_DEB              : $USE_DEB"
echo "EXTRA_DEB            : $EXTRA_DEB"
echo "TEST_PKGS            : $TEST_PKGS"
echo "TARGET_PKGS          : $TARGET_PKGS"
echo "BEFORE_SCRIPT        : $BEFORE_SCRIPT"
echo "NOT_TEST_INSTALL     : $NOT_TEST_INSTALL"
echo "ROS_PARALLEL_JOBS    : $ROS_PARALLEL_JOBS"
echo "ROS_PYTHON_VERSION   : $ROS_PYTHON_VERSION"
echo "CATKIN_PARALLEL_JOBS        : $CATKIN_PARALLEL_JOBS"
echo "CATKIN_TOOLS_BUILD_OPTIONS  : $CATKIN_TOOLS_BUILD_OPTIONS"
echo "CATKIN_TOOLS_CONFIG_OPTIONS : $CATKIN_TOOLS_CONFIG_OPTIONS"
echo "ROS_PARALLEL_TEST_JOBS      : $ROS_PARALLEL_TEST_JOBS"
echo "CATKIN_PARALLEL_TEST_JOBS   : $CATKIN_PARALLEL_TEST_JOBS"
echo "CMAKE_DEVELOPER_ERROR       : $CMAKE_DEVELOPER_ERROR"
echo "BUILD_PKGS           : $BUILD_PKGS"
echo "ROS_REPOSITORY_PATH  : $ROS_REPOSITORY_PATH"
echo "ROSDEP_ADDITIONAL_OPTIONS   : $ROSDEP_ADDITIONAL_OPTIONS"
echo "DOCKER_CONTAINER_NAME       : $DOCKER_CONTAINER_NAME"
echo "DOCKER_RUN_OPTION           : $DOCKER_RUN_OPTION"
echo "NUMBER_OF_LOGS_TO_KEEP      : $NUMBER_OF_LOGS_TO_KEEP"
echo "REPOSITORY_NAME      : $REPOSITORY_NAME"
echo "TRAVIS_BUILD_WEB_URL : $TRAVIS_BUILD_WEB_URL"
echo "TRAVIS_JOB_WEB_URL   : $TRAVIS_JOB_WEB_URL"
echo "DOCKER_IMAGE_JENKINS : $DOCKER_IMAGE_JENKINS"
echo "TIMEOUT_JENKINS      : $TIMEOUT_JENKINS"
echo "ADD_ENV_VALUE_TO_DOCKER     : $ADD_ENV_VALUE_TO_DOCKER"

travis_time_start setup_cache

set -x
# run watchdog for kill orphan docker container
.travis/travis_watchdog.py $DOCKER_CONTAINER_NAME &amp;

# setup cache dir
mkdir -p /data/cache/$ROS_DISTRO/ccache
mkdir -p /data/cache/$ROS_DISTRO/pip-cache
mkdir -p /data/cache/$ROS_DISTRO/chainer
mkdir -p /data/cache/$ROS_DISTRO/ros/data
mkdir -p /data/cache/$ROS_DISTRO/ros/rosdep

# setup docker env-file
DOCKER_ENV_FILE="/tmp/docker_env_file_$$"
: > $DOCKER_ENV_FILE
if [ "$ADD_ENV_VALUE_TO_DOCKER" != "" ]; then
  env_var_list=(`echo "$ADD_ENV_VALUE_TO_DOCKER"`)
  for env_var in ${env_var_list[@]}; do
    echo "$env_var" >> $DOCKER_ENV_FILE
  done
fi
cat $DOCKER_ENV_FILE

travis_time_end

#
docker ps -a
if [ "$(docker ps -a | grep $DOCKER_CONTAINER_NAME || true)" ] ; then
   echo "Reanaming docker container name to $DOCKER_CONTAINER_NAME_$TRAVIS_JENKINS_UNIQUE_ID"
   docker rename $DOCKER_CONTAINER_NAME $DOCKER_CONTAINER_NAME_$TRAVIS_JENKINS_UNIQUE_ID
fi

travis_time_start docker_run

docker run $DOCKER_RUN_OPTION \\
    --name $DOCKER_CONTAINER_NAME \\
    -e ROS_DISTRO="$ROS_DISTRO" \\
    -e USE_DEB="$USE_DEB" \\
    -e TRAVIS_REPO_SLUG="$TRAVIS_REPO_SLUG" \\
    -e EXTRA_DEB="$EXTRA_DEB" \\
    -e TARGET_PKGS="$TARGET_PKGS" \\
    -e BEFORE_SCRIPT="$BEFORE_SCRIPT" \\
    -e TEST_PKGS="$TEST_PKGS" \\
    -e NOT_TEST_INSTALL="$NOT_TEST_INSTALL" \\
    -e ROS_PARALLEL_JOBS="$ROS_PARALLEL_JOBS" \\
    -e ROS_PYTHON_VERSION="$ROS_PYTHON_VERSION" \\
    -e CATKIN_PARALLEL_JOBS="$CATKIN_PARALLEL_JOBS" \\
    -e CATKIN_TOOLS_BUILD_OPTIONS="$CATKIN_TOOLS_BUILD_OPTIONS" \\
    -e CATKIN_TOOLS_CONFIG_OPTIONS="$CATKIN_TOOLS_CONFIG_OPTIONS" \\
    -e ROS_PARALLEL_TEST_JOBS="$ROS_PARALLEL_TEST_JOBS" \\
    -e CATKIN_PARALLEL_TEST_JOBS="$CATKIN_PARALLEL_TEST_JOBS" \\
    -e CMAKE_DEVELOPER_ERROR="$CMAKE_DEVELOPER_ERROR" \\
    -e BUILD_PKGS="$BUILD_PKGS" \\
    -e ROS_REPOSITORY_PATH="$ROS_REPOSITORY_PATH" \\
    -e ROSDEP_ADDITIONAL_OPTIONS="$ROSDEP_ADDITIONAL_OPTIONS" \\
    -e DOCKER_RUN_OPTION="$DOCKER_RUN_OPTION" \\
    -e HOME=/workspace \\
    --env-file $DOCKER_ENV_FILE \\
    -v $WORKSPACE/${BUILD_TAG}:/workspace \\
    -v /data/cache/$ROS_DISTRO/ccache:/workspace/.ccache \\
    -v /data/cache/$ROS_DISTRO/pip-cache:/root/.cache/pip \\
    -v /data/cache/$ROS_DISTRO/chainer:/workspace/.chainer \\
    -v /data/cache/$ROS_DISTRO/ros/data:/workspace/.ros/data \\
    -v /data/cache/$ROS_DISTRO/ros/rosdep:/workspace/.ros/rosdep \\
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \\
    -w /workspace $DOCKER_IMAGE_JENKINS /bin/bash \\
    -c "$(cat &lt;&lt;EOL

cd $TRAVIS_REPO_SLUG
set -x
trap 'exit 1' ERR
env

# setup cache dir
sudo chmod -R a+rw /root/.cache/pip
sudo chown -R root.root /root/.cache/pip
sudo chown -R user.jenkins /workspace/.chainer
sudo chown -R user.jenkins /workspace/.ccache
sudo chown -R user.jenkins /workspace/.ros

# check if archive.ubuntu.com is available in this distribution
sudo apt-get -y -qq update || if [ \$? -eq 100 ]; then sudo sed -i 's/archive.ubuntu.com/old-releases.ubuntu.com/g' /etc/apt/sources.list; fi

# mkdir log dir
mkdir log
export ROS_LOG_DIR=\$PWD/log
ret=1; while [ \$ret != 0 ]; do sudo apt-get update -qq &amp;&amp; ret=0 || echo "apt-get update failed"; done
ret=1; while [ \$ret != 0 ]; do sudo apt-get install -qq -y curl git wget sudo lsb-release ccache apt-cacher-ng apt-utils patch &amp;&amp; ret=0 || echo "apt-get install failed"; done

# setup ccache
sudo ccache -M 30G                   # set maximum size of ccache to 30G

# Enable apt-cacher-ng to cache apt packages
echo 'Acquire::http {proxy "http://$(ifdata -pa docker0):3142"; };' | sudo tee /etc/apt/apt.conf.d/02proxy.conf
# to fix https://github.com/jsk-ros-pkg/jsk_travis/pull/388#issuecomment-549735323
# see https://matoken.org/blog/2019/07/19/direct-access-to-https-repository-with-apt-cacher-ng/
# see https://github.com/sameersbn/docker-apt-cacher-ng/tree/3.1#usage
echo 'Acquire::https {proxy "false"; };' | sudo tee -a /etc/apt/apt.conf.d/02proxy.conf
sudo apt-get update -qq || echo Ignore error of apt-get update
export SHELL=/bin/bash

# Remove warning about camera module
# Reference: http://stackoverflow.com/questions/12689304/ctypes-error-libdc1394-error-failed-to-initialize-libdc1394
sudo ln /dev/null /dev/raw1394

# setup virtual display for GUI testing
# based on http://wiki.ros.org/docker/Tutorials/GUI
export QT_X11_NO_MITSHM=1
export DISPLAY=:0
sudo apt-get install -qq -y mesa-utils
glxinfo | grep GLX || echo "OK"

# start testing
.travis/travis.sh

EOL
)"
rm $DOCKER_ENV_FILE

     </command>
    </hudson.tasks.Shell>
  </builders>
  <publishers/>
  <buildWrappers>
    <hudson.plugins.timestamper.TimestamperBuildWrapper plugin="timestamper@1.5.15"/>
    <hudson.plugins.ansicolor.AnsiColorBuildWrapper plugin="ansicolor@%(ANSICOLOR_PLUGIN_VERSION)s">
      <colorMapName>xterm</colorMapName>
    </hudson.plugins.ansicolor.AnsiColorBuildWrapper>
    <hudson.plugins.build__timeout.BuildTimeoutWrapper plugin="build-timeout@%(TIMEOUT_PLUGIN_VERSION)s">
      <strategy class="hudson.plugins.build_timeout.impl.AbsoluteTimeOutStrategy">
        <timeoutMinutes>%(TIMEOUT_JENKINS)s</timeoutMinutes>
      </strategy>
      <operationList>
        <hudson.plugins.build__timeout.operations.FailOperation/>
      </operationList>
    </hudson.plugins.build__timeout.BuildTimeoutWrapper>
  </buildWrappers>
</project>'''

BUILD_SET_CONFIG= 'job/%(name)s/%(number)d/configSubmit'

class Jenkins(jenkins.Jenkins):
    # http://blog.keshi.org/hogememo/2012/12/14/jenkins-setting-build-info
    def set_build_config(self, name, number, display_name, description): # need to allow anonymous user to update build 
        try:
            parameters = json.dumps({'displayName': display_name, 'description': description})
            response = self.jenkins_open(requests.Request(
                    'POST', self._build_url(BUILD_SET_CONFIG, locals()),
                    data = {'json': parameters}
                ))
            if response:
                return response
            else:
                raise jenkins.JenkinsException('job[%s] number[%d] does not exist'
                                       % (name, number))
        except urllib2.HTTPError:
            raise jenkins.JenkinsException('job[%s] number[%d] does not exist'
                                   % (name, number))
        except ValueError:
            raise jenkins.JenkinsException(
                'Could not parse JSON info for job[%s] number[%d]'
                % (name, number)
            )

# set build configuration
def set_build_configuration(name, number):
    global j

def wait_for_finished(name, number):
    global j
    sleep = 30
    display = 300
    loop = 0
    result = None
    while True :
        now = time.time() * 1000
        try:
            info = j.get_build_info(name, number)
        except jenkins.NotFoundException as e:
            print('ERROR: Jenkins job name={0}, number={1} in server={2}'
                  'not found.'.format(name, number, j.server), file=sys.stderr)
            break
        except jenkins.JenkinsException as e:
            print('ERROR: Maybe Jenkins server is down. Please visit {0}'
                  .format(j.server), file=sys.stderr)
            break
        except Exception as e:
            print('ERROR: Unexpected error: {0}'.format(e), file=sys.stderr)
            break
        if not info['building']:
            result = info['result']
            break
        # update progressbar
        progress = (now - info['timestamp']) / info['estimatedDuration']
        if loop % (display/sleep) == 0:
            print("{} building {}, result: {}, progress: {}".format(info['url'], info['building'], info['result'], progress), file=sys.stderr)
        time.sleep(sleep)
        loop += 1
    return result

def wait_for_building(name, number):
    global j
    sleep = 30
    display = 300
    loop = 0
    start_building = None
    while True:
        try:
            j.get_build_info(name,number)
            start_building = True
            return
        except:
            pass
        if loop % (display/sleep) == 0:
            print('wait for {} {}'.format(name, number), file=sys.stderr)
        time.sleep(sleep)
        loop += 1

##
TRAVIS_BRANCH = env.get('TRAVIS_BRANCH')
TRAVIS_COMMIT = env.get('TRAVIS_COMMIT', 'HEAD')
TRAVIS_PULL_REQUEST = env.get('TRAVIS_PULL_REQUEST', 'false')
TRAVIS_REPO_SLUG = env.get('TRAVIS_REPO_SLUG', 'jsk-ros-pkg/jsk_travis')
TRAVIS_BUILD_ID = env.get('TRAVIS_BUILD_ID')
TRAVIS_BUILD_NUMBER = env.get('TRAVIS_BUILD_NUMBER')
TRAVIS_JOB_ID = env.get('TRAVIS_JOB_ID')
TRAVIS_JOB_NUMBER = env.get('TRAVIS_JOB_NUMBER')
TRAVIS_JENKINS_UNIQUE_ID = '{}.{}.{}'.format(time.time(),TRAVIS_JOB_ID,
                                             ''.join(random.choice(string.digits) for _ in range(16)))

ROS_DISTRO = env.get('ROS_DISTRO', 'indigo')
USE_DEB = env.get('USE_DEB', 'true')
EXTRA_DEB = env.get('EXTRA_DEB', '')
TEST_PKGS = env.get('TEST_PKGS', '')
TARGET_PKGS = env.get('TARGET_PKGS', '')
BEFORE_SCRIPT = env.get('BEFORE_SCRIPT', '')
NOT_TEST_INSTALL = env.get('NOT_TEST_INSTALL', '')
ROS_PARALLEL_JOBS = env.get('ROS_PARALLEL_JOBS', '')
ROS_PYTHON_VERSION = env.get('ROS_PYTHON_VERSION', '')
CATKIN_PARALLEL_JOBS = env.get('CATKIN_PARALLEL_JOBS', '')
CATKIN_TOOLS_BUILD_OPTIONS = env.get('CATKIN_TOOLS_BUILD_OPTIONS', '')
CATKIN_TOOLS_CONFIG_OPTIONS = env.get('CATKIN_TOOLS_CONFIG_OPTIONS', '')
ROS_PARALLEL_TEST_JOBS = env.get('ROS_PARALLEL_TEST_JOBS', '')
CATKIN_PARALLEL_TEST_JOBS = env.get('CATKIN_PARALLEL_TEST_JOBS', '')
CMAKE_DEVELOPER_ERROR = env.get('CMAKE_DEVELOPER_ERROR', '')
BUILD_PKGS = env.get('BUILD_PKGS', '')
ROS_REPOSITORY_PATH = env.get('ROS_REPOSITORY_PATH', '')
ROSDEP_ADDITIONAL_OPTIONS = env.get('ROSDEP_ADDITIONAL_OPTIONS', '')
DOCKER_CONTAINER_NAME = '_'.join([TRAVIS_REPO_SLUG.replace('/','.'), TRAVIS_JOB_NUMBER, TRAVIS_JENKINS_UNIQUE_ID])
DOCKER_RUN_OPTION = env.get('DOCKER_RUN_OPTION', '--rm')
NUMBER_OF_LOGS_TO_KEEP = env.get('NUMBER_OF_LOGS_TO_KEEP', '30')
REPOSITORY_NAME = env.get('REPOSITORY_NAME', '')
TRAVIS_BUILD_WEB_URL = env.get('TRAVIS_BUILD_WEB_URL', '')
TRAVIS_JOB_WEB_URL = env.get('TRAVIS_JOB_WEB_URL', '')
ADDITIONAL_ENV_TO_DOCKER = env.get('ADDITIONAL_ENV_TO_DOCKER', '')
ADD_ENV_VALUE_TO_DOCKER = ''
tmp_list = []
for add_env in ADDITIONAL_ENV_TO_DOCKER.split(' '):
    if add_env != '':
        add_env_val = env.get(add_env, '')
        tmp_list.append(add_env + '=' + add_env_val)
ADD_ENV_VALUE_TO_DOCKER = ' '.join(tmp_list)

if env.get('ROS_DISTRO') == 'hydro':
    LSB_RELEASE = '12.04'
    UBUNTU_DISTRO = 'precise'
elif env.get('ROS_DISTRO') in ['indigo', 'jade']:
    LSB_RELEASE = '14.04'
    UBUNTU_DISTRO = 'trusty'
elif env.get('ROS_DISTRO') in ['kinetic', 'lunar']:
    LSB_RELEASE = '16.04'
    UBUNTU_DISTRO = 'xenial'
elif env.get('ROS_DISTRO') in ['melodic']:
    LSB_RELEASE = '18.04'
    UBUNTU_DISTRO = 'bionic'
elif env.get('ROS_DISTRO') in ['noetic']:
    LSB_RELEASE = '20.04'
    UBUNTU_DISTRO = 'focal'
else:
    LSB_RELEASE = '14.04'
    UBUNTU_DISTRO = 'trusty'

DOCKER_IMAGE_JENKINS = env.get('DOCKER_IMAGE_JENKINS', 'ros-ubuntu:%s-base' % LSB_RELEASE)
TIMEOUT_JENKINS = env.get('TIMEOUT_JENKINS','120')

print('''
TRAVIS_BRANCH        = %(TRAVIS_BRANCH)s
TRAVIS_COMMIT        = %(TRAVIS_COMMIT)s
TRAVIS_PULL_REQUEST  = %(TRAVIS_PULL_REQUEST)s
TRAVIS_REPO_SLUG     = %(TRAVIS_REPO_SLUG)s
TRAVIS_BUILD_ID      = %(TRAVIS_BUILD_ID)s
TRAVIS_BUILD_NUMBER  = %(TRAVIS_BUILD_NUMBER)s
TRAVIS_JOB_ID        = %(TRAVIS_JOB_ID)s
TRAVIS_JOB_NUMBER    = %(TRAVIS_JOB_NUMBER)s
TRAVIS_JENKINS_UNIQUE_ID = %(TRAVIS_JENKINS_UNIQUE_ID)s
ROS_DISTRO       = %(ROS_DISTRO)s
USE_DEB          = %(USE_DEB)s
EXTRA_DEB        = %(EXTRA_DEB)s
TEST_PKGS        = %(TEST_PKGS)s
TARGET_PKGS       = %(TARGET_PKGS)s
BEFORE_SCRIPT      = %(BEFORE_SCRIPT)s
NOT_TEST_INSTALL = %(NOT_TEST_INSTALL)s
ROS_PARALLEL_JOBS       = %(ROS_PARALLEL_JOBS)s
ROS_PYTHON_VERSION       = %(ROS_PYTHON_VERSION)s
CATKIN_PARALLEL_JOBS    = %(CATKIN_PARALLEL_JOBS)s
CATKIN_TOOLS_BUILD_OPTIONS    = %(CATKIN_TOOLS_BUILD_OPTIONS)s
CATKIN_TOOLS_CONFIG_OPTIONS    = %(CATKIN_TOOLS_CONFIG_OPTIONS)s
ROS_PARALLEL_TEST_JOBS  = %(ROS_PARALLEL_TEST_JOBS)s
CATKIN_PARALLEL_TEST_JOBS = %(CATKIN_PARALLEL_TEST_JOBS)s
CMAKE_DEVELOPER_ERROR  = %(CMAKE_DEVELOPER_ERROR)s
BUILD_PKGS       = %(BUILD_PKGS)s
ROS_REPOSITORY_PATH = %(ROS_REPOSITORY_PATH)s
ROSDEP_ADDITIONAL_OPTIONS = %(ROSDEP_ADDITIONAL_OPTIONS)s
DOCKER_CONTAINER_NAME   = %(DOCKER_CONTAINER_NAME)s
DOCKER_RUN_OPTION = %(DOCKER_RUN_OPTION)s
NUMBER_OF_LOGS_TO_KEEP = %(NUMBER_OF_LOGS_TO_KEEP)s
REPOSITORY_NAME = %(REPOSITORY_NAME)s
TRAVIS_BUILD_WEB_URL = %(TRAVIS_BUILD_WEB_URL)s
TRAVIS_JOB_WEB_URL = %(TRAVIS_JOB_WEB_URL)s
DOCKER_IMAGE_JENKINS = %(DOCKER_IMAGE_JENKINS)s
TIMEOUT_JENKINS = %(TIMEOUT_JENKINS)s
ADD_ENV_VALUE_TO_DOCKER = %(ADD_ENV_VALUE_TO_DOCKER)s
''' % locals(), file=sys.stderr)

### start here
j = Jenkins('http://jenkins.jsk.imi.i.u-tokyo.ac.jp:8080/', 'k-okada', '11402334328fd5a26f0092c1d763f67f52')

# use snasi color
if j.get_plugin_info('ansicolor'):
    ANSICOLOR_PLUGIN_VERSION=j.get_plugin_info('ansicolor')['version']
else:
    print('you need to install ansi color plugin', file=sys.stderr)
# use timeout plugin
if j.get_plugin_info('build-timeout'):
    TIMEOUT_PLUGIN_VERSION=j.get_plugin_info('build-timeout')['version']
else:
    print('you need to install build_timeout plugin', file=sys.stderr)
# set job_name
job_name = TRAVIS_REPO_SLUG

job_name = re.sub(r'[^0-9A-Za-z]+', '-', job_name)
# filename must be within 255
if len(job_name) >= 128 : # 'jenkins+ job_naem + TRAVIS_REPO_SLUG'
    import hashlib
    m = hashlib.md5()
    m.update(job_name)
    job_name=job_name[:128]+'-'+m.hexdigest()

if j.job_exists(job_name) is None:
    j.create_job(job_name, jenkins.EMPTY_CONFIG_XML)

## if reconfigure job is already in queue, wait for more seconds...
while [item for item in j.get_queue_info() if item['task']['name'] == job_name]:
    time.sleep(10)
# reconfigure job
# if this fails, check https://github.com/spinnaker/spinnaker/issues/2067#issuecomment-407708770
j.reconfig_job(job_name, CONFIGURE_XML % locals())

## get next number and run
queue_number = j.build_job(job_name, {
    'TRAVIS_BRANCH':TRAVIS_BRANCH,
    'TRAVIS_COMMIT':TRAVIS_COMMIT,
    'TRAVIS_PULL_REQUEST':TRAVIS_PULL_REQUEST,
    'TRAVIS_REPO_SLUG':TRAVIS_REPO_SLUG,
    'TRAVIS_BUILD_ID':TRAVIS_BUILD_ID,
    'TRAVIS_BUILD_NUMBER':TRAVIS_BUILD_NUMBER,
    'TRAVIS_JOB_ID':TRAVIS_JOB_ID,
    'TRAVIS_JOB_NUMBER':TRAVIS_JOB_NUMBER,
    'TRAVIS_JENKINS_UNIQUE_ID':TRAVIS_JENKINS_UNIQUE_ID,
    'ROS_DISTRO':ROS_DISTRO,
    'USE_DEB':USE_DEB,
    'EXTRA_DEB':EXTRA_DEB,
    'TEST_PKGS':TEST_PKGS,
    'TARGET_PKGS':TARGET_PKGS,
    'BEFORE_SCRIPT':BEFORE_SCRIPT,
    'NOT_TEST_INSTALL':NOT_TEST_INSTALL,
    'ROS_PARALLEL_JOBS':ROS_PARALLEL_JOBS,
    'ROS_PYTHON_VERSION':ROS_PYTHON_VERSION,
    'CATKIN_PARALLEL_JOBS':CATKIN_PARALLEL_JOBS,
    'CATKIN_TOOLS_BUILD_OPTIONS':CATKIN_TOOLS_BUILD_OPTIONS,
    'CATKIN_TOOLS_CONFIG_OPTIONS':CATKIN_TOOLS_CONFIG_OPTIONS,
    'ROS_PARALLEL_TEST_JOBS':ROS_PARALLEL_TEST_JOBS,
    'CATKIN_PARALLEL_TEST_JOBS':CATKIN_PARALLEL_TEST_JOBS,
    'CMAKE_DEVELOPER_ERROR':CMAKE_DEVELOPER_ERROR,
    'BUILD_PKGS':BUILD_PKGS,
    'ROS_REPOSITORY_PATH':ROS_REPOSITORY_PATH,
    'ROSDEP_ADDITIONAL_OPTIONS':ROSDEP_ADDITIONAL_OPTIONS,
    'DOCKER_CONTAINER_NAME':DOCKER_CONTAINER_NAME,
    'DOCKER_RUN_OPTION':DOCKER_RUN_OPTION,
    'NUMBER_OF_LOGS_TO_KEEP':NUMBER_OF_LOGS_TO_KEEP,
    'REPOSITORY_NAME':REPOSITORY_NAME,
    'TRAVIS_BUILD_WEB_URL':TRAVIS_BUILD_WEB_URL,
    'TRAVIS_JOB_WEB_URL':TRAVIS_JOB_WEB_URL,
    'DOCKER_IMAGE_JENKINS':DOCKER_IMAGE_JENKINS,
    'TIMEOUT_JENKINS':TIMEOUT_JENKINS,
    'ADD_ENV_VALUE_TO_DOCKER':ADD_ENV_VALUE_TO_DOCKER
})

# wait for queueing
while True:
    message = j.get_queue_item(queue_number)['why']
    if message is None:
        break
    print("wait for queueing ... {} ".format(message.encode('utf-8')), file=sys.stderr)
    time.sleep(3)

# wait for execution
while True:
    item = j.get_queue_item(queue_number)
    if isinstance(item, dict) and 'executable' in item:
        item = item['executable']
        if isinstance(item, dict) and 'number' in item:
            break;
    print("wait for execution.... {}".format(item), file=sys.stderr)
    time.sleep(10)
build_number = item['number']
print('build number is {}'.format(build_number), file=sys.stderr)

## configure description
if TRAVIS_PULL_REQUEST != 'false':
    github_link = 'github <a href=http://github.com/%(TRAVIS_REPO_SLUG)s/pull/%(TRAVIS_PULL_REQUEST)s>PR #%(TRAVIS_PULL_REQUEST)s</a><br>'
elif TRAVIS_BRANCH:
    github_link = 'github <a href=http://github.com/%(TRAVIS_REPO_SLUG)s/tree/%(TRAVIS_BRANCH)s>http://github.com/%(TRAVIS_REPO_SLUG)s</a><br>'
else:
    github_link = 'github <a href=http://github.com/%(TRAVIS_REPO_SLUG)s>http://github.com/%(TRAVIS_REPO_SLUG)s</a><br>'

if TRAVIS_BUILD_WEB_URL and TRAVIS_JOB_WEB_URL:
    travis_link = 'travis <a href=%(TRAVIS_BUILD_WEB_URL)s>Build #%(TRAVIS_BUILD_NUMBER)s</a> '+ '<a href=%(TRAVIS_JOB_WEB_URL)s>Job #%(TRAVIS_JOB_NUMBER)s</a><br>'
else:
    travis_link = 'travis <a href=http://travis-ci.org/%(TRAVIS_REPO_SLUG)s/>%(TRAVIS_REPO_SLUG)s</a><br>'
j.set_build_config(job_name, build_number, '#%(build_number)s %(TRAVIS_REPO_SLUG)s' % locals(),
                   (travis_link + ' \
       Parameters are<br> \
TRAVIS_BRANCH        = %(TRAVIS_BRANCH)s <br> \
TRAVIS_COMMIT        = %(TRAVIS_COMMIT)s <br> \
TRAVIS_PULL_REQUEST  = %(TRAVIS_PULL_REQUEST)s <br> \
TRAVIS_REPO_SLUG     = %(TRAVIS_REPO_SLUG)s <br> \
TRAVIS_BUILD_ID      = %(TRAVIS_BUILD_ID)s <br> \
TRAVIS_BUILD_NUMBER  = %(TRAVIS_BUILD_NUMBER)s <br> \
TRAVIS_JOB_ID        = %(TRAVIS_JOB_ID)s <br> \
TRAVIS_JOB_NUMBER    = %(TRAVIS_JOB_NUMBER)s <br> \
TRAVIS_JENKINS_UNIQUE_ID        = %(TRAVIS_JENKINS_UNIQUE_ID)s <br> \
ROS_DISTRO       = %(ROS_DISTRO)s <br> \
USE_DEB          = %(USE_DEB)s <br> \
EXTRA_DEB        = %(EXTRA_DEB)s <br> \
TEST_PKGS        = %(TEST_PKGS)s <br> \
TARGET_PKGS       = %(TARGET_PKGS)s <br> \
BEFORE_SCRIPT      = %(BEFORE_SCRIPT)s <br> \
NOT_TEST_INSTALL = %(NOT_TEST_INSTALL)s <br> \
ROS_PARALLEL_JOBS       = %(ROS_PARALLEL_JOBS)s <br> \
ROS_PYTHON_VERSION       = %(ROS_PYTHON_VERSION)s <br> \
CATKIN_PARALLEL_JOBS    = %(CATKIN_PARALLEL_JOBS)s <br> \
CATKIN_TOOLS_BUILD_OPTIONS    = %(CATKIN_TOOLS_BUILD_OPTIONS)s <br> \
CATKIN_TOOLS_CONFIG_OPTIONS    = %(CATKIN_TOOLS_CONFIG_OPTIONS)s <br> \
ROS_PARALLEL_TEST_JOBS  = %(ROS_PARALLEL_TEST_JOBS)s <br> \
CATKIN_PARALLEL_TEST_JOBS = %(CATKIN_PARALLEL_TEST_JOBS)s <br> \
CMAKE_DEVELOPER_ERROR  = %(CMAKE_DEVELOPER_ERROR)s <br> \
BUILD_PKGS       = %(BUILD_PKGS)s <br> \
ROS_REPOSITORY_PATH = %(ROS_REPOSITORY_PATH)s <br> \
ROSDEP_ADDITIONAL_OPTIONS = %(ROSDEP_ADDITIONAL_OPTIONS)s <br> \
DOCKER_CONTAINER_NAME   = %(DOCKER_CONTAINER_NAME)s <br> \
DOCKER_RUN_OPTION = %(DOCKER_RUN_OPTION)s <br> \
NUMBER_OF_LOGS_TO_KEEP = %(NUMBER_OF_LOGS_TO_KEEP)s <br> \
REPOSITORY_NAME = %(REPOSITORY_NAME)s <br> \
TRAVIS_BUILD_WEB_URL = %(TRAVIS_BUILD_WEB_URL)s <br> \
TRAVIS_JOB_WEB_URL = %(TRAVIS_JOB_WEB_URL)s <br> \
DOCKER_IMAGE_JENKINS = %(DOCKER_IMAGE_JENKINS)s <br> \
TIMEOUT_JENKINS = %(TIMEOUT_JENKINS)s <br> \
ADD_ENV_VALUE_TO_DOCKER = %(ADD_ENV_VALUE_TO_DOCKER)s <br> \
') % locals())

## wait for result
result = wait_for_finished(job_name, build_number)

## show console
print (u"{}".format(j.get_build_console_output(job_name, build_number)), file=sys.stderr)
print (u"=======================================", file=sys.stderr)
print (u"{}".format(j.get_build_info(job_name, build_number)['url']), file=sys.stderr)
print (u"=======================================", file=sys.stderr)
if result == "SUCCESS" :
    exit(0)
else:
    exit(1)


