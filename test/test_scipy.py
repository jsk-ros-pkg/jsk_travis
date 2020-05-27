#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import unittest
import scipy

class TestNumpy(unittest.TestCase):

    def test_numpy(self):

        print("NumPy : " + scipy.version.full_version, file=sys.stderr)
        print("Python: " + sys.version, file=sys.stderr)
        self.assertTrue('true')

if __name__ == '__main__':
    unittest.main()
