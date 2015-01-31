#!/usr/bin/env python

import jenkins
import urllib
import urllib2
import json
import time
import os
import sys

from os import environ as env

BUILD_SET_CONFIG= 'job/%(name)s/%(number)d/configSubmit'

class Jenkins(jenkins.Jenkins):
    # http://blog.keshi.org/hogememo/2012/12/14/jenkins-setting-build-info
    def set_build_config(self, name, number, display_name, description): # need to allow anonymous user to update build 
        try:
            #print '{{ "displayName": "{}", "description": "{}" }}'.format(display_name, description)
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

def jenkins_open(name):
    global j
    ## start from here
    for item in env.items():
        print('{}={}'.format(item[0], item[1]))
    env['TRAVIS_JENKINS_UNIQUE_ID']='{}.{}'.format(env.get('TRAVIS_JOB_ID'),time.time())
    j.jenkins_open(urllib2.Request(j.build_job_url(name, {'this is dummy': 'parm to call wich "buildWithParameters"'}), urllib.urlencode(env)))

# get build number
def get_build_number(name):
    global j
    unique_id = 'TRAVIS_JENKINS_UNIQUE_ID'
    build_number = False
    while not build_number:
        try:
            numbers = []
            time.sleep(10)
            print('wait for {} ...'.format(env.get(unique_id))),
            for build in j.get_job_info(name)['builds']:
                build_info = j.get_build_info(name, build['number'])
                job_id = [item for item in build_info['actions'][0]['parameters'] if item['name'] == unique_id]
                print(build['number'],job_id and job_id[0] and job_id[0]['value']),
                sys.stdout.flush()
                if job_id :
                    if job_id and job_id[0]['value'] == env.get(unique_id):
                        build_number = int(build['number'])
            print()
            if build_number : return build_number 
        except Exception as e:
            print(e)

# set build configuration
def set_build_configuration(name, number):
    global j
    j.set_build_config(name, number, '#{} {}'.format(number, env.get('TRAVIS_REPO_SLUG')), 
                       'github <a href=http://github.com/{0}/pull/{1}>PR #{1}</a><br>'.format(env.get('TRAVIS_REPO_SLUG'), env.get('TRAVIS_PULL_REQUEST'))+
                       'travis <a href=http://travis-ci.org/{0}/builds/{1}>Build #{2}</a> '.format(env.get('TRAVIS_REPO_SLUG'), env.get('TRAVIS_BUILD_ID'), env.get('TRAVIS_BUILD_NUMBER'))+
                       '<a href=http://travis-ci.org/{0}/builds/{1}>Job #{2}</a><br>'.format(env.get('TRAVIS_REPO_SLUG'), env.get('TRAVIS_JOB_ID'), env.get('TRAVIS_JOB_NUMBER'))+
                       'ROS_DISTRO={}<br>USE_DEB={}<br>'.format(env.get('ROS_DISTRO'),env.get('USE_DEB'))
    )

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

### start here
job_name = 'trusty-travis'
j = Jenkins('http://jenkins.jsk.imi.i.u-tokyo.ac.jp:8080/')
jenkins_open(job_name)
build_number = get_build_number(job_name)
print('build nuber is {}'.format(build_number))
set_build_configuration(job_name, build_number)
result = wait_for_building(job_name, build_number)
print j.get_build_console_output(job_name, build_number)
print "======================================="
print j.get_build_info(job_name, build_number)['url']
print "======================================="
if result == "SUCCESS" :
    exit(0)
else:
    exit(1)


