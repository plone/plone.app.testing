import unittest2 as unittest
import doctest

from plone.testing import layered
from plone.app.testing import layers

OPTIONFLAGS = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        doctest.DocFileSuite('layers.txt', optionflags=OPTIONFLAGS),
        layered(
            doctest.DocFileSuite('helpers.txt',optionflags=OPTIONFLAGS),
            layer=layers.PLONE_INTEGRATION_TESTING,
        ),
    ])
    return suite
