# Helper functions for Plone testing. Also importable from plone.app.testing
# directly

import contextlib

from plone.testing import z2, zca

from plone.app.testing.interfaces import (
        PLONE_SITE_ID,
        SITE_OWNER_USER_NAME
    )

# User management

def login(portal, userName):
    """Log in as the given user in the given Plone site
    """
    
    z2.login(portal['acl_users'], userName)

def logout():
    """Log out, i.e. become anonymous
    """
    
    z2.logout()

def setRoles(portal, userName, roles):
    """Set the given user's roles to a tuple of roles.
    """
    
    userFolder = portal['acl_users']
    z2.setRoles(userFolder, userName, roles)

# Product management - helpers to tear down state

def tearDownProfileRegistation(productName):
    """Remove all profiles for the given product in the global GenericSetup
    profile registry. Does nothing if no profile is associated with this
    product.
    
    This helper is useful during tear-down if a product has explicitly added
    a registration to the GenericSetup ``_profile_registry``, or used the
    ``<genericsetup:registerProfile />`` ZCML directive.
    """
    
    simpleProductName = None
    if productName.startswith('Products.'):
        simpleProductName = productName[9:]
    
    # Look for profiles added to the _profileRegistry and remove
    from Products.GenericSetup.registry import _profile_registry
    profilesToRemove = set()
    for profileId, profileInfo in _profile_registry._profile_info.items():
        if profileInfo['product'] in (productName, simpleProductName):
            profilesToRemove.add(profileId)
    for profileId in profilesToRemove:
        del _profile_registry._profile_info[profileId]
        _profile_registry._profile_ids.remove(profileId)

def tearDownMultiPluginRegistration(pluginName):
    """Remove the given PAS MultiPlugin name from the global PAS registry.
    Does nothing if the plugin name is not registered.
    
    This helper is useful during tear-down if a product has explicitly added
    a MultiPlugin registraton to the PluggableAuthService using the
    ``<pas:registerMultiPlugin />`` ZCML directive.
    """
    
    from Products.PluggableAuthService import PluggableAuthService
    
    if pluginName in PluggableAuthService.MultiPlugins:
        PluggableAuthService.MultiPlugins.remove(pluginName)

# Product management - local site

def quickInstallProduct(portal, productName, reinstall=False):
    """Install a product using the ``portal_quickinstaller`` tool. If
    ``reinstall`` is false and the product is already installed, do nothing.
    If ``reinstall`` is true, perform an explicit reinstall if the product
    is installed already.
    """
    
    from AccessControl import getSecurityManager, setSecurityManager
    sm = getSecurityManager()
    
    login(portal, SITE_OWNER_USER_NAME)
    
    try:
        quickinstaller = portal['portal_quickinstaller']
        
        if quickinstaller.isProductInstalled(productName):
            if reinstall:
                quickinstaller.reinstallProduct([productName])
        else:
            quickinstaller.installProduct(productName)
        
        portal.clearCurrentSkin()
        portal.setupCurrentSkin(portal.REQUEST)
        
    finally:
        setSecurityManager(sm)

def installProfile(portal, profileName):
    """Install an extension profile into the portal. The profile name
    should be a package name and a profile name, e.g. 'my.product:default'.
    """
    
    from AccessControl import getSecurityManager, setSecurityManager
    sm = getSecurityManager()
    
    login(portal, SITE_OWNER_USER_NAME)
    
    try:
        setupTool = portal['portal_setup']
        profileId = 'profile-%s' % (profileName,)
        setupTool.runAllImportStepsFromProfile(profileId)
        
        portal.clearCurrentSkin()
        portal.setupCurrentSkin(portal.REQUEST)
        
    finally:
        setSecurityManager(sm)

# Component architecture

def pushGlobalRegistry(portal, new=None, name=None):
    """Set a new global component registry that uses the current registry as
    a a base. If you use this, you *must* call ``popGlobalRegistry()`` to
    restore the original state.
    
    If ``new`` is not given, a new registry is created. If given, you must
    provide a ``zope.component.globalregistry.BaseGlobalComponents`` object.
    
    Returns the new registry.
    
    Also ensure that the persistent component registry at ``portal`` has the
    new global registry as its base.
    """
    
    current = zca.pushGlobalRegistry(new=new)
    
    from five.localsitemanager import update_sitemanager_bases
    update_sitemanager_bases(portal)
    
    return current
    
def popGlobalRegistry(portal):
    """Restore the global component registry form the top of the stack, as
    set with ``pushGlobalRegistry()``.
    
    Also ensure that the persistent component registry at ``portal`` has the
    new global registry as its base.
    """
    
    previous = zca.popGlobalRegistry()
    
    from five.localsitemanager import update_sitemanager_bases
    update_sitemanager_bases(portal)
    
    return previous

@contextlib.contextmanager
def ploneSite(db=None, connection=None, environ=None):
    """Context manager for working with the Plone portal during layer setup::
    
        with ploneSite() as portal:
            ...
    
    This is based on the ``z2.zopeApp()`` context manager. See the module
     ``plone.testing.z2`` for details.
    
    Do not use this in a test. Use the 'portal' resource from the PloneSite
    layer instead!
    
    Pass a ZODB handle as ``db`` to use a specificdatabase. Alternatively,
    pass an open connection as ``connection`` (the connection will not be
    closed).
    """
    
    with z2.zopeApp(db, connection, environ) as app:
        yield app[PLONE_SITE_ID]
