#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest


class TestEnvVar(unittest.TestCase):

    def test_env_var(self):

        self.assertTrue(os.getenv('TEST_VAR1', '') == 'true')
        self.assertTrue(os.getenv('TEST_VAR2', '') == 'false')


if __name__ == '__main__':
    unittest.main()
