#!/usr/bin/env python

from base import LintingBase
from manifest import LintingManifest


def lint_packages(pkg_paths):
    for pkg_path in pkg_paths:
        linter = LintingManifest(pkg_path)()
    LintingBase.report()
