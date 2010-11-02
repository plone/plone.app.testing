import unittest2 as unittest
import doctest

OPTIONFLAGS = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE


# Dummy handler used in tests
def dummy(context):
    pass


def test_suite():
    suite = unittest.TestSuite()
    seltest = doctest.DocFileSuite('selenium.txt', optionflags=OPTIONFLAGS)
    # Run selenium tests on level 2, as it requires a correctly configured
    # Firefox browser
    seltest.level = 2
    suite.addTests([
        doctest.DocFileSuite('cleanup.txt', optionflags=OPTIONFLAGS),
        doctest.DocFileSuite('layers.txt', optionflags=OPTIONFLAGS),
        doctest.DocFileSuite('helpers.txt', optionflags=OPTIONFLAGS),
        seltest,
    ])
    return suite
