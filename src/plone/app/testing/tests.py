import doctest
import unittest


OPTIONFLAGS = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE


# Dummy handler used in tests
def dummy(context):
    pass


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
            ),
            doctest.DocFileSuite(
                "layers.rst",
                optionflags=OPTIONFLAGS,
            ),
            doctest.DocFileSuite(
                "helpers.rst",
                optionflags=OPTIONFLAGS,
            ),
        ]
    )
    return suite
