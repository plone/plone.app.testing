# -*- coding: utf-8 -*-
import doctest
import re
import six
import unittest


OPTIONFLAGS = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE


# Dummy handler used in tests
def dummy(context):
    pass


class Py23DocChecker(doctest.OutputChecker):
    def check_output(self, want, got, optionflags):
        if six.PY2:
            got = re.sub("u'(.*?)'", "'\\1'", got)
        return doctest.OutputChecker.check_output(self, want, got, optionflags)


def test_suite():
    suite = unittest.TestSuite()
    # seltest = doctest.DocFileSuite('selenium.rst', optionflags=OPTIONFLAGS)
    # Run selenium tests on level 2, as it requires a correctly configured
    # Firefox browser
    # seltest.level = 2
    suite.addTests(
        [
            doctest.DocFileSuite(
                "cleanup.rst",
                optionflags=OPTIONFLAGS,
                checker=Py23DocChecker(),
            ),
            doctest.DocFileSuite(
                "layers.rst",
                optionflags=OPTIONFLAGS,
                checker=Py23DocChecker(),
            ),
            doctest.DocFileSuite(
                "helpers.rst",
                optionflags=OPTIONFLAGS,
                checker=Py23DocChecker(),
            ),
        ]
    )
    if six.PY2:
        suite.addTests([
            doctest.DocFileSuite(
                'layers_zserver.rst', optionflags=OPTIONFLAGS),
        ])
    return suite
