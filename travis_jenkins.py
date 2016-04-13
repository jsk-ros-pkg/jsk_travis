#!/usr/bin/env python

# need pip installed version of python-jenkins > 0.4.0

import jenkins
import urllib
import urllib2
import json
import time
import os
import sys
from xml.sax.saxutils import escape
from xml.sax.saxutils import unescape

from os import environ as env

CONFIGURE_XML = '''<?xml version='1.0' encoding='UTF-8'?>
<project>
  <actions/>
  <description>
     &lt;h4&gt;
     This is jenkins buildfirm for &lt;a href=http://github.com/%(TRAVIS_REPO_SLUG)s&gt;http://github.com/%(TRAVIS_REPO_SLUG)s&lt;/a&gt;&lt;br/&gt;
     see &lt;a href=http://travis-ci.org/%(TRAVIS_REPO_SLUG)s&gt;http://travis-ci.org/%(TRAVIS_REPO_SLUG)s&lt;/a&gt; for travis page that execute this job.&lt;br&gt;
     &lt;/h4&gt;
     Parameters are&lt;br&gt;
       ROS_DISTRO = %(ROS_DISTRO)s&lt;br&gt;
       ROSWS      = %(ROSWS)s&lt;br&gt;
       BUILDIER   = %(BUILDER)s&lt;br&gt;
       USE_DEB    = %(USE_DEB)s&lt;br&gt;
       EXTRA_DEB  = %(EXTRA_DEB)s&lt;br&gt;
       TARGET_PKGS = %(TARGET_PKGS)s&lt;br&gt;
       BEFORE_SCRIPT = %(BEFORE_SCRIPT)s&lt;br&gt;
       TEST_PKGS  = %(TEST_PKGS)s&lt;br&gt;
       NOT_TEST_INSTALL = %(NOT_TEST_INSTALL)s&lt;br&gt;
       ROS_PARALLEL_JOBS = %(ROS_PARALLEL_JOBS)s&lt;br&gt;
       CATKIN_PARALLEL_JOBS = %(CATKIN_PARALLEL_JOBS)s&lt;br&gt;
       ROS_PARALLEL_TEST_JOBS = %(ROS_PARALLEL_TEST_JOBS)s&lt;br&gt;
       CATKIN_PARALLEL_TEST_JOBS = %(CATKIN_PARALLEL_TEST_JOBS)s&lt;br&gt;
       BUILDING_PKG = %(BUILD_PKGS)s&lt;br&gt;
  </description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <jenkins.model.BuildDiscarderProperty>
      <strategy class="hudson.tasks.LogRotator">
        <daysToKeep>3</daysToKeep>
        <numToKeep>3</numToKeep>
        <artifactDaysToKeep>-1</artifactDaysToKeep>
        <artifactNumToKeep>-1</artifactNumToKeep>
      </strategy>
    </jenkins.model.BuildDiscarderProperty>
    <hudson.model.ParametersDefinitionProperty>
      <parameterDefinitions>
        <hudson.model.TextParameterDefinition>
          <name>TRAVIS_JENKINS_UNIQUE_ID</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>TRAVIS_PULL_REQUEST</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
        <hudson.model.TextParameterDefinition>
          <name>TRAVIS_COMMIT</name>
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
set -x
set -e
env
WORKSPACE=`pwd`
[ "${BUILD_TAG}" = "" ] &amp;&amp; BUILD_TAG="build_tag" # jenkins usually has build_tag environment, note this is sh
trap "pwd; sudo rm -fr $WORKSPACE/${BUILD_TAG} || echo 'ok'" EXIT

# try git clone until success
until git clone http://github.com/%(TRAVIS_REPO_SLUG)s ${BUILD_TAG}/%(TRAVIS_REPO_SLUG)s
do
  echo "Retrying"
done
cd ${BUILD_TAG}/%(TRAVIS_REPO_SLUG)s
#git fetch -q origin '+refs/pull/*:refs/remotes/pull/*'
#git checkout -qf %(TRAVIS_COMMIT)s || git checkout -qf pull/${TRAVIS_PULL_REQUEST}/head
if [ "${TRAVIS_PULL_REQUEST}" != "false" ]; then
 git fetch origin +refs/pull/${TRAVIS_PULL_REQUEST}/merge
 git checkout -qf FETCH_HEAD
else
 git checkout -qf ${TRAVIS_COMMIT}
fi

git submodule init
git submodule update

# remove containers created/exited more than 48 hours ago
for container in `sudo docker ps -a | egrep '^.*days ago' | awk '{print $1}'`; do
     sudo docker rm $container || echo ok
done

sudo docker stop %(DOCKER_CONTAINER_NAME)s || echo "docker stop %(DOCKER_CONTAINER_NAME)s ends with $?"
sudo docker rm %(DOCKER_CONTAINER_NAME)s || echo  "docker rm %(DOCKER_CONTAINER_NAME)s ends with $?"
sudo docker run -t --name %(DOCKER_CONTAINER_NAME)s -e ROS_DISTRO='%(ROS_DISTRO)s' -e ROSWS='%(ROSWS)s' -e BUILDER='%(BUILDER)s' -e USE_DEB='%(USE_DEB)s' -e TRAVIS_REPO_SLUG='%(TRAVIS_REPO_SLUG)s' -e EXTRA_DEB='%(EXTRA_DEB)s' -e TARGET_PKGS='%(TARGET_PKGS)s' -e BEFORE_SCRIPT='%(BEFORE_SCRIPT)s' -e TEST_PKGS='%(TEST_PKGS)s' -e NOT_TEST_INSTALL='%(NOT_TEST_INSTALL)s' -e ROS_PARALLEL_JOBS='%(ROS_PARALLEL_JOBS)s' -e CATKIN_PARALLEL_JOBS='%(CATKIN_PARALLEL_JOBS)s' -e ROS_PARALLEL_TEST_JOBS='%(ROS_PARALLEL_TEST_JOBS)s' -e CATKIN_PARALLEL_TEST_JOBS='%(CATKIN_PARALLEL_TEST_JOBS)s' -e BUILD_PKGS='%(BUILD_PKGS)s'  -e HOME=/workspace -v $WORKSPACE/${BUILD_TAG}:/workspace -v /export/data1/ccache:/workspace/.ccache -v /export/data1/pip-cache:/workspace/.cache/pip -v /export/data1/ros_test_data:/workspace/.ros/test_data -w /workspace ros-ubuntu:%(LSB_RELEASE)s /bin/bash -c "$(cat &lt;&lt;EOL

cd %(TRAVIS_REPO_SLUG)s
set -x
trap 'exit 1' ERR
env

mkdir log
export ROS_LOG_DIR=\$PWD/log
apt-get update -qq || echo Ignore error of apt-get update
apt-get install -qq -y git wget sudo lsb-release ccache  apt-cacher-ng

# setup ccache
ccache -M 20G                   # set maximum size of ccache to 20G

# Enable apt-cacher-ng to cache apt packages
echo 'Acquire::http {proxy "http://$(ifdata -pa docker0):3142"; };' > /etc/apt/apt.conf.d/02proxy.conf
apt-get update -qq || echo Ignore error of apt-get update
export SHELL=/bin/bash

# Remove warning about camera module
# Reference: http://stackoverflow.com/questions/12689304/ctypes-error-libdc1394-error-failed-to-initialize-libdc1394
sudo ln /dev/null /dev/raw1394

`cat .travis/travis.sh`

EOL
)"

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
        <timeoutMinutes>120</timeoutMinutes>
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
            # print '{{ "displayName": "{}", "description": "{}" }}'.format(display_name, description)
            response = self.jenkins_open(urllib2.Request(
                self.server + BUILD_SET_CONFIG % locals(),
                urllib.urlencode({'json': '{{ "displayName": "{}", "description": "{}" }}'.format(display_name, description)})
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
    while True :
        try:
            info = j.get_build_info(name, number)
            if info['building'] is False: return info['result']
        except Exception, e:
            print(e)
        if loop % (display/sleep) == 0:
            print info['url'], "building..", info['building'], "result...", info['result']
        time.sleep(sleep)
        loop += 1

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
            print('wait for {} {}'.format(name, number))
        time.sleep(sleep)
        loop += 1


def escape_1depth(string):
    """Escape with assumption of 1 depth recursiveness.

    >>> escape_1depth('&amp;')
    &amp;
    >>> escape_1depth('&')
    &amp;

    """
    return escape(unescape(string))


##
TRAVIS_BRANCH   = escape_1depth(env.get('TRAVIS_BRANCH'))
TRAVIS_COMMIT   = escape_1depth(env.get('TRAVIS_COMMIT', 'HEAD'))
TRAVIS_PULL_REQUEST     = escape_1depth(env.get('TRAVIS_PULL_REQUEST', 'false'))
TRAVIS_REPO_SLUG        = escape_1depth(env.get('TRAVIS_REPO_SLUG', 'jsk-ros-pkg/jsk_travis'))
TRAVIS_BUILD_ID         = escape_1depth(env.get('TRAVIS_BUILD_ID')
TRAVIS_BUILD_NUMBER     = escape_1depth(env.get('TRAVIS_BUILD_NUMBER'))
TRAVIS_JOB_ID           = escape_1depth(env.get('TRAVIS_JOB_ID'))
TRAVIS_JOB_NUMBER       = escape_1depth(env.get('TRAVIS_JOB_NUMBER'))
ROS_DISTRO      = escape_1depth(env.get('ROS_DISTRO', 'indigo'))
ROSWS           = escape_1depth(env.get('ROSWS', 'wstool'))
BUILDER         = escape_1depth(env.get('BUILDER', 'catkin'))
USE_DEB         = escape_1depth(env.get('USE_DEB', 'true'))
EXTRA_DEB       = escape_1depth(env.get('EXTRA_DEB', ''))
TEST_PKGS       = escape_1depth(env.get('TEST_PKGS', ''))
TARGET_PKGS     = escape_1depth(env.get('TARGET_PKGS', ''))
BEFORE_SCRIPT   = escape_1depth(env.get('BEFORE_SCRIPT', ''))
NOT_TEST_INSTALL        = escape_1depth(unescape(env.get('NOT_TEST_INSTALL', '')))
ROS_PARALLEL_JOBS       = escape_1depth(env.get('ROS_PARALLEL_JOBS', ''))
CATKIN_PARALLEL_JOBS    = escape_1depth(env.get('CATKIN_PARALLEL_JOBS', ''))
ROS_PARALLEL_TEST_JOBS  = escape_1depth(env.get('ROS_PARALLEL_TEST_JOBS', ''))
CATKIN_PARALLEL_TEST_JOBS = escape_1depth(env.get('CATKIN_PARALLEL_TEST_JOBS', ''))
BUILD_PKGS       = escape_1depth(env.get('BUILD_PKGS', ''))
DOCKER_CONTAINER_NAME = escape_1depth('_'.join([TRAVIS_REPO_SLUG.replace('/','.'), TRAVIS_JOB_NUMBER]))

print('''
TRAVIS_BRANCH        = %(TRAVIS_BRANCH)s
TRAVIS_COMMIT        = %(TRAVIS_COMMIT)s
TRAVIS_PULL_REQUEST  = %(TRAVIS_PULL_REQUEST)s
TRAVIS_REPO_SLUG     = %(TRAVIS_REPO_SLUG)s
TRAVIS_BUILD_ID      = %(TRAVIS_BUILD_ID)s
TRAVIS_BUILD_NUMBER  = %(TRAVIS_BUILD_NUMBER)s
TRAVIS_JOB_ID        = %(TRAVIS_JOB_ID)s
TRAVIS_JOB_NUMBER    = %(TRAVIS_JOB_NUMBER)s
TRAVIS_BRANCH        = %(TRAVIS_BRANCH)s
ROS_DISTRO       = %(ROS_DISTRO)s
ROSWS            = %(ROSWS)s
BUILDER          = %(BUILDER)s
USE_DEB          = %(USE_DEB)s
EXTRA_DEB        = %(EXTRA_DEB)s
TEST_PKGS        = %(TEST_PKGS)s
TARGET_PKGS       = %(TARGET_PKGS)s
BEFORE_SCRIPT      = %(BEFORE_SCRIPT)s
NOT_TEST_INSTALL = %(NOT_TEST_INSTALL)s
ROS_PARALLEL_JOBS       = %(ROS_PARALLEL_JOBS)s
CATKIN_PARALLEL_JOBS    = %(CATKIN_PARALLEL_JOBS)s
ROS_PARALLEL_TEST_JOBS  = %(ROS_PARALLEL_TEST_JOBS)s
CATKIN_PARALLEL_TEST_JOBS = %(CATKIN_PARALLEL_TEST_JOBS)s
BUILD_PKGS       = %(BUILD_PKGS)s
DOCKER_CONTAINER_NAME   = %(DOCKER_CONTAINER_NAME)s
''' % locals())

if env.get('ROS_DISTRO') == 'hydro':
    LSB_RELEASE = '12.04'
elif env.get('ROS_DISTRO') == 'indigo':
    LSB_RELEASE = '14.04'
elif env.get('ROS_DISTRO') == 'jade':
    LSB_RELEASE = '14.04'
elif env.get('ROS_DISTRO') == 'kinetic':
    LSB_RELEASE = '16.04'
else:
    LSB_RELEASE = '14.04'

### start here
j = Jenkins('http://jenkins.jsk.imi.i.u-tokyo.ac.jp:8080/', 'k-okada', '22f8b1c4812dad817381a05f41bef16b')

# use snasi color
if j.get_plugin_info('ansicolor'):
    ANSICOLOR_PLUGIN_VERSION=j.get_plugin_info('ansicolor')['version']
else:
    print('you need to install ansi color plugin')
# use timeout plugin
if j.get_plugin_info('build-timeout'):
    TIMEOUT_PLUGIN_VERSION=j.get_plugin_info('build-timeout')['version']
else:
    print('you need to install build_timeout plugin')
# set job_name
job_name = '-'.join(filter(bool, ['trusty-travis',TRAVIS_REPO_SLUG, ROS_DISTRO, 'deb', USE_DEB, EXTRA_DEB, NOT_TEST_INSTALL, BUILD_PKGS])).replace('/','-').replace(' ','-')
if j.job_exists(job_name) is None:
    j.create_job(job_name, jenkins.EMPTY_CONFIG_XML)

## if reconfigure job is already in queue, wait for more seconds...
while [item for item in j.get_queue_info() if item['task']['name'] == job_name]:
    time.sleep(10)
# reconfigure job
j.reconfig_job(job_name, CONFIGURE_XML % locals())

## get next number and run
build_number = j.get_job_info(job_name)['nextBuildNumber']
TRAVIS_JENKINS_UNIQUE_ID='{}.{}'.format(TRAVIS_JOB_ID,time.time())

j.build_job(job_name, {'TRAVIS_JENKINS_UNIQUE_ID':TRAVIS_JENKINS_UNIQUE_ID, 'TRAVIS_PULL_REQUEST':TRAVIS_PULL_REQUEST, 'TRAVIS_COMMIT':TRAVIS_COMMIT})
print('next build number is {}'.format(build_number))

## wait for starting
result = wait_for_building(job_name, build_number)
print('start building, wait for result....')

## configure description
if TRAVIS_PULL_REQUEST != 'false':
    github_link = 'github <a href=http://github.com/%(TRAVIS_REPO_SLUG)s/pull/%(TRAVIS_PULL_REQUEST)s>PR #%(TRAVIS_PULL_REQUEST)s</a><br>'
elif TRAVIS_BRANCH:
    github_link = 'github <a href=http://github.com/%(TRAVIS_REPO_SLUG)s/tree/%(TRAVIS_BRANCH)s>http://github.com/%(TRAVIS_REPO_SLUG)s</a><br>'
else:
    github_link = 'github <a href=http://github.com/%(TRAVIS_REPO_SLUG)s>http://github.com/%(TRAVIS_REPO_SLUG)s</a><br>'

if TRAVIS_BUILD_ID and TRAVIS_JOB_ID:
    travis_link = 'travis <a href=http://travis-ci.org/%(TRAVIS_REPO_SLUG)s/builds/%(TRAVIS_BUILD_ID)s>Build #%(TRAVIS_BUILD_NUMBER)s</a> '+ '<a href=http://travis-ci.org/%(TRAVIS_REPO_SLUG)s/jobs/%(TRAVIS_JOB_ID)s>Job #%(TRAVIS_JOB_NUMBER)s</a><br>'
else:
    travis_link = 'travis <a href=http://travis-ci.org/%(TRAVIS_REPO_SLUG)s/>%(TRAVIS_REPO_SLUG)s</a><br>'
j.set_build_config(job_name, build_number, '#%(build_number)s %(TRAVIS_REPO_SLUG)s' % locals(),
                   (github_link + travis_link +'ROS_DISTRO=%(ROS_DISTRO)s<br>USE_DEB=%(USE_DEB)s<br>') % locals())

## wait for result
result = wait_for_finished(job_name, build_number)

## show console
print j.get_build_console_output(job_name, build_number)
print "======================================="
print j.get_build_info(job_name, build_number)['url']
print "======================================="
if result == "SUCCESS" :
    exit(0)
else:
    exit(1)


