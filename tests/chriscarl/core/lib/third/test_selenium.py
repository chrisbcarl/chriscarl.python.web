#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author:         Chris Carl
Email:          chrisbcarl@outlook.com
Date:           2026-01-19
Description:

chriscarl.core.lib.third.selenium unit test.

Updates:
    2026-01-19 - tests.chriscarl.core.lib.third.selenium - initial commit
'''

# stdlib imports (expected to work)
from __future__ import absolute_import, print_function, division, with_statement  # , unicode_literals
import os
import sys
import logging
import unittest

# third party imports
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# project imports (expected to work)
from chriscarl.core import constants
from chriscarl.core.lib.stdlib.os import abspath
from chriscarl.core.lib.stdlib.unittest import UnitTest
from chriscarl.core.functors.parse.html import html_to_dom

# test imports
import chriscarl.core.lib.third.selenium as lib

SCRIPT_RELPATH = 'tests/chriscarl/core/lib/third/test_selenium.py'
if not hasattr(sys, '_MEIPASS'):
    SCRIPT_FILEPATH = os.path.abspath(__file__)
else:
    SCRIPT_FILEPATH = os.path.abspath(os.path.join(sys._MEIPASS, SCRIPT_RELPATH))  # pylint: disable=no-member
SCRIPT_DIRPATH = os.path.dirname(SCRIPT_FILEPATH)
SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]
THIS_MODULE = sys.modules[__name__]
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

constants.fix_constants(lib)  # deal with namespace sharding the files across directories


class TestCase(UnitTest):

    def setUp(self):
        self.driver, self.wait = lib.get_driver()
        self.index_html = abspath(constants.MAIN_TESTS_COLLATERAL_DIRPATH, 'index.html')
        return super().setUp()

    def tearDown(self):
        self.driver.close()
        return super().tearDown()

    # @unittest.skip('lorem ipsum')
    def test_case_0(self):
        self.driver.get('https://example.com')
        anchor = lib.wait_for(self.wait, By.TAG_NAME, 'a')
        variables = [
            (lib.web_element_getattr, (anchor, 'href')),
            (lib.web_element_getattr, (anchor, 'plz')),
        ]
        controls = [
            'https://iana.org/domains/example',
            AttributeError,
        ]
        self.assert_null_hypothesis(variables, controls)

    def test_case_1(self):
        self.driver.get('https://example.com')
        anchor_selenium = lib.wait_for(self.wait, By.TAG_NAME, 'a')
        html_filepath, _ = lib.save_page(self.driver, output_dirpath=self.tempdir)
        dom = html_to_dom(html_filepath)
        anchor_text = dom.get_element_by_tag('a')
        self.assertEqual(lib.web_element_getattr(anchor_selenium, 'href'), anchor_text.attrs['href'])

    def test_case_2(self):
        variables = [
            (lib.driver_get_status, (self.driver, 'https://example.com')),
            (lib.driver_get_status, (self.driver, f'file:///{self.index_html}')),
        ]
        controls = [
            200,
            200,
        ]
        self.assert_null_hypothesis(variables, controls)

    def test_case_3(self):
        lib.driver_get_status(self.driver, 'https://example.com')
        results = [
            lib.find_one_element(self.driver, By.TAG_NAME, 'span'),  # does not exist
            lib.find_one_element(self.driver, By.TAG_NAME, 'p'),  # exist
            lib.find_one_element(self.driver, By.TAG_NAME, 'span', 'a', 'h1'),  # a exist
            lib.find_one_element_from_groups(
                self.driver,
                (By.XPATH, '//*[@id]'),  # not exist
                (By.TAG_NAME, 'span'),  # not exist
                (By.TAG_NAME, 'a'),  # idx will be returned
                (By.TAG_NAME, 'p'),
            ),
            lib.find_one_element_from_groups(
                self.driver,
                (By.XPATH, '//*[@id]'),  # not exist
                (By.TAG_NAME, 'span'),  # not exist
                (By.TAG_NAME, 'a'),  # idx will be returned
                (By.TAG_NAME, 'p'),
                everything=True,
            ),
        ]
        variables = [((lambda x: x[1]), (tpl, )) for tpl in results]
        controls = [
            -1,
            0,
            1,
            2,
            -1,  # not everything exists, so nothing is returned
        ]
        self.assert_null_hypothesis(variables, controls)


if __name__ == '__main__':
    tc = TestCase()
    tc.setUp()

    try:
        tc.test_case_0()
        tc.test_case_1()
        tc.test_case_2()
        tc.test_case_3()
    finally:
        tc.tearDown()
