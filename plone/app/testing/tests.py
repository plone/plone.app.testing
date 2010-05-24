import unittest2 as unittest
import doctest

OPTIONFLAGS = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE

# Dummy handler used in tests
def dummy(context):
    pass

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        doctest.DocFileSuite('cleanup.txt', optionflags=OPTIONFLAGS),
        doctest.DocFileSuite('layers.txt',  optionflags=OPTIONFLAGS),
        doctest.DocFileSuite('helpers.txt', optionflags=OPTIONFLAGS),
    ])
    return suite
