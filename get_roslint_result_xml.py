#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import re
import shlex
import subprocess
from subprocess import Popen
from subprocess import PIPE


def get_commits_from_origin():
    cmd = 'git log --format="%h" origin/master..'
    commits = subprocess.check_output(shlex.split(cmd)).splitlines()
    return commits


def get_changed_files_from_origin():
    cmd = r"git log --name-status origin/master.. | grep -E '^[A-Z]\b'"
    files = subprocess.check_output(cmd, shell=True).splitlines()
    files = [f.split('\t')[-1] for f in files]
    return files


def get_changed_line_of_commit(commit, files):
    cmd = 'git blame {}'
    for f in files:
        if not os.path.isfile(f):
            continue
        blame = subprocess.check_output(shlex.split(cmd.format(f)))
        for i, line in enumerate(blame.splitlines()):
            line_num = i + 1
            if re.search('^' + commit, line):
                return commit, f, line_num


def get_buildspace():
    pref_path = os.getenv('CMAKE_PREFIX_PATH').split(':')[0]
    buildspace = os.path.join(os.path.dirname(pref_path), 'build')
    return buildspace


def get_roslint_results(pkg):
    cwd = os.path.join(get_buildspace(), pkg)
    if not os.path.exists(cwd):
        print("[{pkg}] buildspace '{space}' does not exist"
              .format(pkg=pkg, space=cwd))
        return []
    cmd = 'make roslint'
    p = Popen(shlex.split(cmd), cwd=cwd,
              stdin=None, stdout=None, stderr=PIPE, close_fds=True)
    results = []
    for line in p.stderr.readlines():
        m = re.match('(.*?):([0-9].*?):  (.*?)$', line)
        if m is None:
            continue
        fname, line_num, message = m.groups()
        results.append((fname, int(line_num), message))
    return results


def compose_report_xml(reports, repo_slug, pr_num):
    owner, repo = repo_slug.split('/')
    xml = '<roslint>'
    xml += '''\
<remote>
  <github owner="{owner}" repository="{repo}" pullrequest="{pr_num}" />
</remote>
<result>
'''.format(owner=owner, repo=repo, pr_num=pr_num)
    results = []
    for rep in reports:
        fname, commit, line_num, message = rep
        result = '''\
<file path="{path}" commit="{commit}">
  <error line="{line_num}">{msg}</error>
</file>
'''.format(path=fname, commit=commit, line_num=line_num, msg=message)
        results.append(result)
    xml += '\n'.join(results)
    xml += '</result>\n</roslint>\n'
    return xml


def get_roslint_result_xml(packages, repo_slug, pr_num, output):
    commits = get_commits_from_origin()
    files = get_changed_files_from_origin()
    diff_lines = []
    for commit in commits:
        changed_line = get_changed_line_of_commit(commit, files)
        if changed_line is not None:
            diff_lines.append(changed_line)

    lint_results = []
    for pkg in packages:
        lint_results.extend(get_roslint_results(pkg))
    lint_reports = []
    for commit, fname0, line_num0 in diff_lines:
        for fname1, line_num1, message in lint_results:
            if os.path.abspath(fname0) == fname1 and line_num0 == line_num1:
                lint_reports.append((fname0, commit, line_num0, message))
    xml = compose_report_xml(lint_reports, repo_slug, pr_num)
    with open(output, 'w') as f:
        f.write(xml)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('packages', nargs='+')
    parser.add_argument('--repo-slug', required=True)
    parser.add_argument('--pr-number', required=True)
    parser.add_argument('--out-file', required=True)
    args = parser.parse_args()
    get_roslint_result_xml(
        args.packages, args.repo_slug, args.pr_number, output=args.out_file)


if __name__ == '__main__':
    main()
