#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuki Furuta <furushchev@jsk.imi.i.u-tokyo.ac.jp>

from __future__ import print_function
import os
import sys
from argparse import ArgumentParser
import httplib2
from xml.etree import ElementTree
try:
    import simplejson as json
except ImportError:
    import json


class CommentLintResult(object):
    def __init__(self, cache_dir, github_token):
        self.client = httplib2.Http(cache_dir)
        self.github_token = github_token
    def run(self, input_path):
        x = ElementTree.parse(input_path)
        if x.find(".//remote/github") != None:
            self.get_github_info(x)
        else:
            print("No remote information found", file=sys.stderr)
            return False
        
        for f in x.iterfind(".//result/file"):
            try:
                self.criticize(f)
            except Exception as e:
                print("Error: %s" % e)
                return False
        print("All codes are criticized")
        return True

    def get_github_info(self, xml):
        github = xml.find(".//remote/github")
        self.owner = github.get("owner")
        self.repo = github.get("repository")
        self.pr_num = github.get("pullrequest")

    def criticize(self, file_element):
        path = file_element.get("path")
        commit_id = file_element.get("commit")
        for e in list(file_element):
            pos = e.get("line")
            body = "[%s] %s" % (e.tag.title(), e.text)
            self.send_comment(self.owner,
                              self.repo,
                              self.pr_num,
                              body, commit_id, path, pos)

    def send_comment(self, owner, repo, pr_num, body, commit_id, path, position):
        if type(position) is not int:
            position = int(position)
        # POST /repos/:owner/:repo/pulls/:number/comments
        urlpath = os.path.join("https://api.github.com",
                               "repos", owner, repo,
                               "pulls", pr_num, "comments")
        headers = {"Accept":"application/vnd.github.v3.full+json",
                   "Content-Type": "application/json",
                   "Authorization": "token " + self.github_token}
        data = {"body": body,
                "commit_id": commit_id,
                "path": path,
                "position": position}
        print("sending request to %s" % urlpath)
        res, content = self.client.request(urlpath, "POST",
                                           headers=headers,
                                           body=json.dumps(data))
        content = json.loads(content)
        if "message" not in content:
            content["message"] = content["url"]
        print("received response [%s] %s" % (res["status"], content["message"]))
        if "errors" in content:
            print("Error: failed to send comment: %s" % content["errors"], file=sys.stderr)
            return False
        else:
            return True

if __name__ == '__main__':
    p = ArgumentParser()
    p.add_argument("-i", dest="input_path", default=None, required=True,
                 help="path to output xml file of linter")
    p.add_argument("-c", dest="cache_dir", default=".cache",
                 help="path to cache directory")
    p.add_argument("-t", dest="token", default=None, required=True,
                 help="github token for comment")
    o = p.parse_args()
    if not os.path.exists(o.input_path):
        p.error("file %s not exists" % o.input_path)
        sys.exit(1)

    c = CommentLintResult(cache_dir=o.cache_dir, github_token=o.token)
    if c.run(input_path=o.input_path):
        sys.exit(0)
    else:
        sys.exit(1)
