from __future__ import print_function

import sys


class LintingBase(object):

    reports = []

    def __init__(self, pkg_path):
        self.pkg_path = pkg_path

    def __call__(self):
        for method in dir(self):
            if method.startswith('lint_'):
                getattr(self, method)()

    def add_report(self, msg, file=''):
        report = '${file}: ${msg}'
        report = report.replace('${msg}', msg)
        report = report.replace('${file}' if file else '${file}: ', file)
        self.reports.append(report)

    @classmethod
    def report(cls):
        for report in cls.reports:
            print(report, file=sys.stderr)
        if cls.reports:
            sys.exit(1)
