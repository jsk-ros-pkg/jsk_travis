from collections import Counter
import os

from catkin_pkg.packages import parse_package

from base import LintingBase


class LintingManifest(LintingBase):

    def __init__(self, pkg_path):
        super(LintingManifest, self).__init__(pkg_path)
        self.manifest_file = os.path.join(pkg_path, 'package.xml')

    def add_report(self, msg):
        super(LintingManifest, self).add_report(msg, file=self.manifest_file)

    def lint_depends(self):
        manifest = parse_package(self.manifest_file)

        buildtool_deps = [dep.name for dep in manifest.buildtool_depends]
        dups = [pkg for pkg, cnt in Counter(buildtool_deps).items()
                if cnt != 1]
        if dups:
            self.add_report('<buildtool_depend> has duplication')
        if buildtool_deps != sorted(buildtool_deps):
            self.add_report('<buildtool_depend> must be sorted')

        build_deps = [dep.name for dep in manifest.build_depends]
        dups = [pkg for pkg, cnt in Counter(build_deps).items() if cnt != 1]
        if dups:
            self.add_report('<build_depend> has duplication')
        if build_deps != sorted(build_deps):
            self.add_report('<build_depend> must be sorted')

        exec_deps = [dep.name for dep in manifest.exec_depends]
        dups = [pkg for pkg, cnt in Counter(exec_deps).items() if cnt != 1]
        if dups:
            self.add_report('<run_depend> has duplication')
        if exec_deps != sorted(exec_deps):
            self.add_report('<run_depend> must be sorted')
