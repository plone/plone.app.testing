"""Cleanup handlers for various global registries
"""

from zope.testing.cleanup import addCleanUp

def cleanUpProfileRegistry():
    try:
        from Products.GenericSetup.registry import _profile_registry
    except ImportError:
        pass
    else:
        _profile_registry.clear()

addCleanUp(cleanUpProfileRegistry)

def cleanUpMultiPlugins():
    try:
        from Products.PluggableAuthService.PluggableAuthService import MultiPlugins
    except ImportError:
        pass
    else:
        del MultiPlugins[:]

addCleanUp(cleanUpMultiPlugins)
