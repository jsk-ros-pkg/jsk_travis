#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuki Furuta <furushchev@jsk.imi.i.u-tokyo.ac.jp>

from __future__ import print_function
import argparse
import json
import os
import subprocess
import sys
import threading
import traceback
import urllib2


EXIT_CODE_ON_ERROR=0 # exit with 0 not to bother build process

class TravisWatchdog(object):
    def __init__(self, travis_job_id, docker_container_name, pro, interval, token, sudo):
        self.travis_job_id = travis_job_id
        self.docker_container_name = docker_container_name
        self.watch_interval = interval
        self.travis_api_token = token
        self.sudo = sudo
        self.pro = pro
        if self.travis_job_id is None:
            print("travis_job_id is not set", file=sys.stderr)
            exit(EXIT_CODE_ON_ERROR)
        if self.pro:
            if self.travis_api_token is None:
                print("travis_api_token is not set", file=sys.stderr)
                exit(EXIT_CODE_ON_ERROR)
            self.travis_api_uri = "https://api.travis-ci.com"
        else:
            self.travis_api_uri = "https://api.travis-ci.org"
    def run(self):
        try:
            if self.fetch_travis_run_state():
                self.stop_docker_container()
                self.remove_docker_container()
                exit(0)
            threading.Timer(self.watch_interval, self.run).start()
        except Exception as e:
            print("Error:", str(e), file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            exit(EXIT_CODE_ON_ERROR)
    def fetch_travis_run_state(self):
        uri = os.path.join(self.travis_api_uri, "jobs", self.travis_job_id)
        req = urllib2.Request(uri)
        if self.pro:
            req.add_header("Authentication", "token %s" % self.travis_api_token)
        res = json.load(urllib2.urlopen(req))
        if "state" not in res:
            raise Exception("not found key: state")
        return res["state"] == "started"
    def stop_docker_container(self):
        cmd = "docker stop %s" % self.docker_container_name
        if self.sudo:
            cmd = "sudo %s" % cmd
        print("Stopping docker container:", self.docker_container_name)
        subprocess.check_call(cmd, shell=True)
        print("Stopped docker container:", self.docker_container_name)
    def remove_docker_container(self):
        cmd = "docker rm %s" % self.docker_container_name
        if self.sudo:
            cmd = "sudo %s" % cmd
        print("Removing docker container:", self.docker_container_name)
        subprocess.check_call(cmd, shell=True)
        print("Removed docker container:", self.docker_container_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Watchdog travis and kill docker")
    parser.add_argument("docker_container_name",
                        help="Docker container name to kill")
    parser.add_argument("travis_job_id",
                        help="Travis JOB ID (default: env TRAVIS_JOB_ID)",
                        nargs="?",
                        default=os.environ.get("TRAVIS_JOB_ID", None))
    parser.add_argument("-i", "--interval",
                        help="Interval for watching travis job status [sec] (default: 10)",
                        type=int,
                        default=10)
    parser.add_argument("--sudo",
                        help="use sudo to kill docker container",
                        action="store_true")
    parser.add_argument("--pro",
                        help="use travis-ci.com instead of travis-ci.org",
                        action="store_true")
    parser.add_argument("--token",
                        help="Travis API token for access to private repositories (default: env TRAVIS_API_TOKEN)",
                        type=str,
                        default=os.environ.get("TRAVIS_API_TOKEN", None))
    args = parser.parse_args()
    worker = TravisWatchdog(**parser.parse_args().__dict__)
    worker.run()

