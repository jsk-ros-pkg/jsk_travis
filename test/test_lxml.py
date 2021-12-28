#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import unittest

class TestLexml(unittest.TestCase):

    def test_lxml(self):

        import lxml
        print(lxml)
        self.assertTrue('true')

if __name__ == '__main__':
    unittest.main()
