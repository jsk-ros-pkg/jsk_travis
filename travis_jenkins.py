#!/usr/bin/env python

# need pip installed version of python-jenkins > 0.4.0

import jenkins
import urllib
import urllib2
import json
import time
import os
import sys

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
       NOT_TEST_INSTALL = %(NOT_TEST_INSTALL)s&lt;br&gt;
       BUILDING_PKG = %(BUILD_PKG)s&lt;br&gt;
  </description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <scm class='hudson.scm.NullSCM'/>
  <assignedNode>master</assignedNode>
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers/>
  <concurrentBuild>false</concurrentBuild>
  <builders>
    <hudson.tasks.Shell>
      <command>
set -x
set -e

WORKSPACE=`pwd`
trap "pwd; sudo rm -fr $WORKSPACE/%(BUILD_TAG)s || echo 'ok'" EXIT

git clone http://github.com/%(TRAVIS_REPO_SLUG)s %(BUILD_TAG)s/%(TRAVIS_REPO_SLUG)s
cd %(BUILD_TAG)s/%(TRAVIS_REPO_SLUG)s
#git fetch -q origin '+refs/pull/*:refs/remotes/pull/*'
#git checkout -qf %(TRAVIS_COMMIT)s || git checkout -qf pull/%(TRAVIS_PULL_REQUEST)s/head
if [ "%(TRAVIS_PULL_REQUEST)s" != "false" ]; then
 git fetch origin +refs/pull/%(TRAVIS_PULL_REQUEST)s/merge
 git checkout -qf FETCH_HEAD
else
 git checkout -qf %(TRAVIS_COMMIT)s
fi


git submodule init
git submodule update

sudo docker rm `sudo docker ps --no-trunc -a -q` || echo "ok"
sudo docker rmi $(sudo docker images | awk '/^&lt;none&gt;/ { print $3 }') || echo "oK"

sudo docker run -t -e ROS_DISTRO=%(ROS_DISTRO)s -e ROSWS=%(ROSWS)s -e BUILDER=%(BUILDER)s -e USE_DEB=%(USE_DEB)s -e TRAVIS_REPO_SLUG=%(TRAVIS_REPO_SLUG)s -e EXTRA_DEB="%(EXTRA_DEB)s" -e NOT_TEST_INSTALL=%(NOT_TEST_INSTALL)s -e BUILD_PKGS="%(BUILD_PKG)s"  -e HOME=/workspace -v $WORKSPACE/%(BUILD_TAG)s:/workspace -w /workspace ros-ubuntu:14.04 /bin/bash -c "$(cat &lt;&lt;EOL

cd %(TRAVIS_REPO_SLUG)s
set -x
trap 'exit 1' ERR
env

apt-get install -qq -y git wget sudo lsb-release
rosdep update || rosdep update || echo "OK"

export SHELL=/bin/bash
`cat .travis/travis.sh`

EOL
)"

     </command>
    </hudson.tasks.Shell>
  </builders>
  <publishers/>
  <buildWrappers/>
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

def wait_for_building(name, number):
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
        print loop

BUILD_TAG       = env.get('BUILD_TAG') or 'build_tag'
TRAVIS_BRANCH   = env.get('TRAVIS_BRANCH') or 'master'
TRAVIS_COMMIT   = env.get('TRAVIS_COMMIT') or 'HEAD'
TRAVIS_PULL_REQUEST     = env.get('TRAVIS_PULL_REQUEST') or 'false'
TRAVIS_REPO_SLUG        = env.get('TRAVIS_REPO_SLUG') or 'jsk-ros-pkg/jsk_travis'
ROS_DISTRO      = env.get('ROS_DISTRO') or 'indigo'
ROSWS           = env.get('ROSWS') or 'wstool'
BUILDER         = env.get('BUILDER') or 'catkin'
USE_DEB         = env.get('USE_DEB') or 'true'
EXTRA_DEB       = env.get('EXTRA_DEB') or ''
NOT_TEST_INSTALL        = env.get('NOT_TEST_INSTALL') or ''
BUILD_PKG       = env.get('BUILD_PKG') or ''

### start here
j = Jenkins('http://jenkins.jsk.imi.i.u-tokyo.ac.jp:8080/', 'k-okada', '22f8b1c4812dad817381a05f41bef16b')
job_name = '-'.join(filter(bool, ['trusty-travis',TRAVIS_REPO_SLUG, ROS_DISTRO, 'deb', USE_DEB, EXTRA_DEB, NOT_TEST_INSTALL, BUILD_PKG])).replace('/','-').replace(' ','-')
if j.job_exists(job_name) is None:
    print "create"
    j.create_job(job_name, jenkins.EMPTY_CONFIG_XML)

## reconfigure job
j.reconfig_job(job_name, CONFIGURE_XML % locals())

## get next number and run
build_number = j.get_job_info(job_name)['nextBuildNumber']
j.build_job(job_name)
print('next build nuber is {}'.format(build_number))

## wait for starting
start_building = None
while not start_building:
    try:
        j.get_build_info(job_name, build_number)
        start_building = True
    except:
        time.sleep(10)
        pass

## configure description
TRAVIS_BUILD_ID = env.get('TRAVIS_BUILD_ID')
TRAVIS_BUILD_NUMBER = env.get('TRAVIS_BUILD_NUMBER')
TRAVIS_JOB_ID = env.get('TRAVIS_JOB_ID')
TRAVIS_JOB_NUMBER = env.get('TRAVIS_JOB_NUMBER')
TRAVIS_BRANCH = env.get('TRAVIS_BRANCH')
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
                   (github_link + travis_link +'ROS_DISTRO=%(ROS_DISTRO)s<br>%(USE_DEB)s<br>') % locals())

## wait for result
result = wait_for_building(job_name, build_number)

## show console
print j.get_build_console_output(job_name, build_number)
print "======================================="
print j.get_build_info(job_name, build_number)['url']
print "======================================="
if result == "SUCCESS" :
    exit(0)
else:
    exit(1)


