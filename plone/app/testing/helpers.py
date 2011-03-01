# Helper functions for Plone testing. Also importable from plone.app.testing
# directly

import contextlib

from zope.configuration import xmlconfig

from plone.testing import z2, zodb, zca, security, Layer

from plone.app.testing import layers
from plone.app.testing.interfaces import (
        PLONE_SITE_ID,
        SITE_OWNER_NAME,
        TEST_USER_NAME,
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

def setRoles(portal, userId, roles):
    """Set the given user's roles to a tuple of roles.
    """

    userFolder = portal['acl_users']
    z2.setRoles(userFolder, userId, roles)

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
    from Products.PluggableAuthService import zcml

    if pluginName in PluggableAuthService.MultiPlugins:
        PluggableAuthService.MultiPlugins.remove(pluginName)

    if pluginName in zcml._mt_regs:
        zcml._mt_regs.remove(pluginName)

# Product management - local site

def quickInstallProduct(portal, productName, reinstall=False):
    """Install a product using the ``portal_quickinstaller`` tool. If
    ``reinstall`` is false and the product is already installed, do nothing.
    If ``reinstall`` is true, perform an explicit reinstall if the product
    is installed already.
    """

    from Acquisition import aq_parent
    from AccessControl import getSecurityManager
    from AccessControl.SecurityManagement import setSecurityManager

    sm = getSecurityManager()
    app = aq_parent(portal)

    z2.login(app['acl_users'], SITE_OWNER_NAME)

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

def applyProfile(portal, profileName):
    """Install an extension profile into the portal. The profile name
    should be a package name and a profile name, e.g. 'my.product:default'.
    """

    from Acquisition import aq_parent
    from AccessControl import getSecurityManager
    from AccessControl.SecurityManagement import setSecurityManager

    sm = getSecurityManager()
    app = aq_parent(portal)

    z2.login(app['acl_users'], SITE_OWNER_NAME)

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
    a base. If you use this, you *must* call ``popGlobalRegistry()`` to
    restore the original state.

    If ``new`` is not given, a new registry is created. If given, you must
    provide a ``zope.component.globalregistry.BaseGlobalComponents`` object.

    Returns the new registry.

    Also ensure that the persistent component registry at ``portal`` has the
    new global registry as its base.
    """

    from zope.site.hooks import setSite, getSite, setHooks
    site = getSite()

    localSiteManager = portal.getSiteManager()

    current = zca.pushGlobalRegistry(new=new)

    if current not in localSiteManager.__bases__:
        localSiteManager.__bases__ = (current,)

    if site is not None:
        setHooks()
        setSite(site)

    return current

def popGlobalRegistry(portal):
    """Restore the global component registry form the top of the stack, as
    set with ``pushGlobalRegistry()``.

    Also ensure that the persistent component registry at ``portal`` has the
    new global registry as its base.
    """

    # First, check if the component site has the global site manager in its
    # bases. If so, that site manager is about to disappear, so set its
    # base(s) as the new base(s) for the local site manager.

    from zope.component import getGlobalSiteManager
    globalSiteManager = getGlobalSiteManager()

    gsmBases = globalSiteManager.__bases__

    from zope.site.hooks import setSite, getSite, setHooks
    site = getSite()

    localSiteManager = portal.getSiteManager()

    bases = []
    changed = False
    for base in localSiteManager.__bases__:
        if base is globalSiteManager:
            bases.extend(gsmBases)
            changed = True
        else:
            bases.append(base)

    if changed:
        localSiteManager.__bases__ = tuple(bases)

    # Now pop the registry. We need to do it in this somewhat convoluted way
    # to avoid the risk of unpickling errors

    previous = zca.popGlobalRegistry()

    if site is not None:
        setHooks()
        setSite(site)

    return previous

@contextlib.contextmanager
def ploneSite(db=None, connection=None, environ=None):
    """Context manager for working with the Plone portal during layer setup::

        with ploneSite() as portal:
            ...

    This is based on the ``z2.zopeApp()`` context manager. See the module
     ``plone.testing.z2`` for details.

    Do not use this in a test. Use the 'portal' resource from the PloneFixture
    layer instead!

    Pass a ZODB handle as ``db`` to use a specificdatabase. Alternatively,
    pass an open connection as ``connection`` (the connection will not be
    closed).
    """

    from zope.site.hooks import setSite, getSite, setHooks
    setHooks()

    site = getSite()

    with z2.zopeApp(db, connection, environ) as app:
        portal = app[PLONE_SITE_ID]

        setSite(portal)
        login(portal, TEST_USER_NAME)

        try:
            yield portal
        finally:
            logout()
            if site is not portal:
                setSite(site)

# Layer base class

class PloneSandboxLayer(Layer):
    """Layer base class managing the common pattern of having a stacked ZODB
    ``DemoStorage`` and a stacked global component registry for the layer.

    Base classes must override and implemented ``setUpPloneSite()``. They
    may also implement ``tearDownPloneSite()``, and can optionally change
    the ``defaultBases`` tuple.
    """

    # The default list of bases.

    defaultBases = (layers.PLONE_FIXTURE,)

    # Hooks

    def setUpZope(self, app, configurationContext):
        """Set up Zope.

        ``app`` is the Zope application root.

        ``configurationContext`` is the ZCML configuration context.

        This is the most appropriate place to load ZCML or install Zope 2-
        style products, using the ``plone.testing.z2.installProduct`` helper.
        """
        pass

    def tearDownZope(self, app):
        """Tear down Zope.

        ``app`` is the Zope application root.

        This is the most appropriate place to uninstall Zope 2-style products
        using the ``plone.testing.z2.uninstallProduct`` helper.
        """
        pass

    def setUpPloneSite(self, portal):
        """Set up the Plone site.

        ``portal`` is the Plone site. Provided no exception is raised, changes
        to this site will be committed (into a newly stacked ``DemoStorage``).

        Concrete layer classes should implement this method at a minimum.
        """
        pass

    def tearDownPloneSite(self, portal):
        """Tear down the Plone site.

        Implementing this is optional. If the changes made during the
        ``setUpPloneSite()`` method were confined to the ZODB and the global
        component regsitry, those changes will be torn down automatically.
        """

        pass

    # Boilerplate

    def setUp(self):

        # Push a new database storage so that database changes
        # commited during layer setup can be easily torn down
        self['zodbDB'] = zodb.stackDemoStorage(self.get('zodbDB'), name=self.__name__)

        # Push a new configuration context so that it's possible to re-import
        # ZCML files after tear-down
        self['configurationContext'] = configurationContext = zca.pushConfigurationContext()

        with ploneSite() as portal:

            from zope.site.hooks import setSite, setHooks
            setHooks()

            # Make sure there's no local site manager while we load ZCML
            setSite(None)

            # Push a new component registry so that ZCML registations
            # and other global component registry changes are sandboxed
            pushGlobalRegistry(portal)

            # Make sure zope.security checkers can be set up and torn down
            # reliably

            security.pushCheckers()

            # Snapshot the GenericSetup profiles registry before loading
            # the custom configuration

            from Products.GenericSetup.registry import _profile_registry
            from Products.GenericSetup.registry import _import_step_registry
            from Products.GenericSetup.registry import _export_step_registry

            preSetupProfiles     = list(_profile_registry._profile_ids)
            preSetupImportSteps  = list(_import_step_registry.listSteps())
            preSetupExportSteps  = list(_export_step_registry.listSteps())

            from Products.PluggableAuthService.PluggableAuthService import MultiPlugins

            preSetupMultiPlugins = MultiPlugins[:]

            # Allow subclass to load ZCML and products
            self.setUpZope(portal.getPhysicalRoot(), configurationContext)

            # Allow subclass to configure a persistent fixture
            setSite(portal)
            self.setUpPloneSite(portal)
            setSite(None)

        # Keep track of profiles that were added during setup
        self.snapshotProfileRegistry(preSetupProfiles, preSetupImportSteps, preSetupExportSteps)

        # Keep track of PAS plugins that were added during setup
        self.snapshotMultiPlugins(preSetupMultiPlugins)

    def tearDown(self):

        with z2.zopeApp() as app:

            portal = app[PLONE_SITE_ID]

            from zope.site.hooks import setSite, setHooks
            setHooks()
            setSite(portal)

            # Allow subclass to tear down persistent fixture
            self.tearDownPloneSite(portal)

            setSite(None)

            # Make sure zope.security checkers can be set up and torn down
            # reliably

            security.popCheckers()

            # Pop the component registry, thus removing component
            # architecture registrations
            popGlobalRegistry(portal)

            # Remove PAS plugins
            self.tearDownMultiPlugins()

            # Remove global profile registrations
            self.tearDownProfileRegistry()

            # Allow subclass to tear down products
            self.tearDownZope(app)

        # Zap the configuration context
        zca.popConfigurationContext()
        del self['configurationContext']

        # Pop the demo storage, thus restoring the database to the
        # previous state
        self['zodbDB'].close()
        del self['zodbDB']

    # Helpers
    def applyProfile(self, portal, profileName):
        return applyProfile(portal, profileName)

    def loadZCML(self, name='configure.zcml', **kw):
        kw.setdefault('context', self['configurationContext'])
        return xmlconfig.file(name, **kw)

    def snapshotProfileRegistry(self, preSetupProfiles, preSetupImportSteps, preSetupExportSteps):
        """Save a snapshot of all profiles that were added during setup, by
        comparing to the list of profiles passed in.
        """

        self._addedProfiles = set()
        self._addedImportSteps = set()
        self._addedExportSteps = set()

        from Products.GenericSetup.registry import _profile_registry
        from Products.GenericSetup.registry import _import_step_registry
        from Products.GenericSetup.registry import _export_step_registry

        for profileId in _profile_registry._profile_ids:
            if profileId not in preSetupProfiles:
                self._addedProfiles.add(profileId)

        for stepId in _import_step_registry.listSteps():
            if stepId not in preSetupImportSteps:
                self._addedImportSteps.add(stepId)

        for stepId in _export_step_registry.listSteps():
            if stepId not in preSetupExportSteps:
                self._addedExportSteps.add(stepId)

    def tearDownProfileRegistry(self):
        """Delete all profiles that were added during setup, as stored by
        ``snapshotProfileRegistry()``.
        """

        from Products.GenericSetup.registry import _profile_registry
        from Products.GenericSetup.registry import _import_step_registry
        from Products.GenericSetup.registry import _export_step_registry

        for profileId in self._addedProfiles:
            if profileId in _profile_registry._profile_ids:
                _profile_registry._profile_ids.remove(profileId)
            if profileId in _profile_registry._profile_info:
                del _profile_registry._profile_info[profileId]

        for stepId in self._addedImportSteps:
            if stepId in _import_step_registry.listSteps():
                _import_step_registry.unregisterStep(stepId)

        for stepId in self._addedExportSteps:
            if stepId in _export_step_registry.listSteps():
                _export_step_registry.unregisterStep(stepId)

    def snapshotMultiPlugins(self, preSetupMultiPlugins):
        """Save a snapshot of all PAS multi plugins that were added during
        setup, by comparing to the list of plugins passed in.
        """

        self._addedMultiPlugins = set()

        from Products.PluggableAuthService.PluggableAuthService import MultiPlugins

        for plugin in MultiPlugins:
            if plugin not in preSetupMultiPlugins:
                self._addedMultiPlugins.add(plugin)

    def tearDownMultiPlugins(self):
        """Delete all PAS multi plugins that were added during setup, as
        stored by ``snapshotMultiPlugins()``.
        """

        for pluginName in self._addedMultiPlugins:
            tearDownMultiPluginRegistration(pluginName)
