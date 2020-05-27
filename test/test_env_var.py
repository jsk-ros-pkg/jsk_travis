#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import sys
import unittest


class TestEnvVar(unittest.TestCase):

    def test_env_var(self):

        print("TEST_VAR1 : " + os.getenv('TEST_VAR1', ''), file=sys.stderr)
        print("TEST_VAR2 : " + os.getenv('TEST_VAR2', ''), file=sys.stderr)
        self.assertTrue(os.getenv('TEST_VAR1', '') == 'true')
        self.assertTrue(os.getenv('TEST_VAR2', '') == 'false')


if __name__ == '__main__':
    unittest.main()
