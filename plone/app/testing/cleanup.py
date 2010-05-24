"""Cleanup handlers for various global registries
"""

from zope.testing.cleanup import addCleanUp

# Make sure cleanup handlers from GenericSetup are registered
try:
    import Products.GenericSetup.zcml
except ImportError:
    pass

def cleanUpGenericSetupRegistries():
    try:
        from Products.GenericSetup import registry
    except ImportError:
        pass
    else:
        registry._import_step_registry.clear()
        registry._export_step_registry.clear()
        registry._profile_registry.clear()

addCleanUp(cleanUpGenericSetupRegistries)

def cleanUpMultiPlugins():
    try:
        from Products.PluggableAuthService.PluggableAuthService import MultiPlugins
    except ImportError:
        pass
    else:
        del MultiPlugins[:]

addCleanUp(cleanUpMultiPlugins)
del addCleanUp