#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import unittest
import numpy

class TestNumpy(unittest.TestCase):

    def test_numpy(self):

        print("NumPy : ", numpy.version.full_version)
        print("Python: ", sys.version)
        self.assertTrue('true')

if __name__ == '__main__':
    unittest.main()
