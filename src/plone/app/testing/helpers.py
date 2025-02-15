# Helper functions for Plone testing. Also importable from plone.app.testing
# directly

from plone.app.testing import layers
from plone.app.testing.interfaces import PLONE_SITE_ID
from plone.app.testing.interfaces import SITE_OWNER_NAME
from plone.app.testing.interfaces import TEST_USER_NAME
from plone.testing import Layer
from plone.testing import security
from plone.testing import zca
from plone.testing import zodb
from plone.testing import zope
from zope.component import getGlobalSiteManager
from zope.component.hooks import getSite
from zope.component.hooks import setHooks
from zope.component.hooks import setSite
from zope.configuration import xmlconfig

import contextlib


# User management


def login(portal, userName):
    """Log in as the given user in the given Plone site"""

    zope.login(portal["acl_users"], userName)


def logout():
    """Log out, i.e. become anonymous"""

    zope.logout()


def setRoles(portal, userId, roles):
    """Set the given user's roles to a tuple of roles."""

    userFolder = portal["acl_users"]
    zope.setRoles(userFolder, userId, roles)


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
    """Install a product using the add-ons control panel (portal setup).

    If ``reinstall`` is false and the product is already installed, do nothing.
    If ``reinstall`` is true, perform an uninstall and install if the product
    is installed already.
    """

    from AccessControl import getSecurityManager
    from AccessControl.SecurityManagement import setSecurityManager
    from Acquisition import aq_parent

    sm = getSecurityManager()
    app = aq_parent(portal)

    zope.login(app["acl_users"], SITE_OWNER_NAME)

    from Products.CMFPlone.utils import get_installer

    qi = get_installer(portal)

    try:
        if not qi.is_product_installed(productName):
            qi.install_product(productName, allow_hidden=True)
        elif reinstall:
            qi.uninstall_product(productName)
            qi.install_product(productName, allow_hidden=True)

        portal.clearCurrentSkin()
        portal.setupCurrentSkin(portal.REQUEST)

    finally:
        setSecurityManager(sm)


def applyProfile(
    portal,
    profileName,
    purge_old=None,
    ignore_dependencies=False,
    archive=None,
    blacklisted_steps=None,
):
    """Install an extension profile into the portal. The profile name
    should be a package name and a profile name, e.g. 'my.product:default'.
    """

    from AccessControl import getSecurityManager
    from AccessControl.SecurityManagement import setSecurityManager
    from Acquisition import aq_parent

    sm = getSecurityManager()
    app = aq_parent(portal)

    zope.login(app["acl_users"], SITE_OWNER_NAME)

    try:
        setupTool = portal["portal_setup"]
        profileId = f"profile-{profileName}"
        setupTool.runAllImportStepsFromProfile(
            profileId,
            purge_old=purge_old,
            ignore_dependencies=ignore_dependencies,
            archive=archive,
            blacklisted_steps=blacklisted_steps,
        )

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
    globalSiteManager = getGlobalSiteManager()
    gsmBases = globalSiteManager.__bases__
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


def persist_profile_upgrade_versions(portal):
    """Persist the profile_upgrade_versions of portal_setup.

    Until at least Products.GenericSetup 1.8.3 this is a standard
    non-persistent dictionary, which means a transaction rollback does
    not rollback changes to this dictionary.  So we make it a persistent
    mapping.  Call this once in layer setup and you have easy rollback.
    """
    from persistent.mapping import PersistentMapping

    puv = portal.portal_setup._profile_upgrade_versions
    if isinstance(puv, PersistentMapping):
        return
    portal.portal_setup._profile_upgrade_versions = PersistentMapping(puv)


@contextlib.contextmanager
def ploneSite(db=None, connection=None, environ=None, flavour=zope):
    """Context manager for working with the Plone portal during layer setup::

        with ploneSite() as portal:
            ...

    This is based on the ``zope.zopeApp()`` context manager. See the module
     ``plone.testing.zope`` for details.

    Do not use this in a test. Use the 'portal' resource from the PloneFixture
    layer instead!

    Pass a ZODB handle as ``db`` to use a specificdatabase. Alternatively,
    pass an open connection as ``connection`` (the connection will not be
    closed).

    flavour ... either `plone.testing.zope` for WSGI
                or `plone.testing.zserver` for ZServer
    """
    setHooks()
    site = getSite()

    with getattr(flavour, "zopeApp")(db, connection, environ) as app:
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
        style products, using the ``plone.testing.zope.installProduct`` helper.
        """
        pass

    def tearDownZope(self, app):
        """Tear down Zope.

        ``app`` is the Zope application root.

        This is the most appropriate place to uninstall Zope 2-style products
        using the ``plone.testing.zope.uninstallProduct`` helper.
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
        component registry, those changes will be torn down automatically.
        """

        pass

    # Boilerplate

    def setUp(self):
        try:
            # Push a new database storage so that database changes
            # committed during layer setup can be easily torn down
            self["zodbDB"] = zodb.stackDemoStorage(
                self.get("zodbDB"), name=self.__name__
            )

            # Push a new configuration context so that it's possible to
            # re-import ZCML files after tear-down
            name = self.__name__ if self.__name__ is not None else "not-named"
            contextName = f"PloneSandboxLayer-{name}"
            self["configurationContext"] = configurationContext = (
                zca.stackConfigurationContext(
                    self.get("configurationContext"), name=contextName
                )
            )

            with ploneSite() as portal:
                setHooks()

                # Make sure there's no local site manager while we load ZCML
                setSite(None)

                # Push a new component registry so that ZCML registrations
                # and other global component registry changes are sandboxed
                pushGlobalRegistry(portal)

                # Persist GenericSetup profile upgrade versions for easy
                # rollback.
                persist_profile_upgrade_versions(portal)

                # Make sure zope.security checkers can be set up and torn down
                # reliably

                security.pushCheckers()

                from Products.PluggableAuthService.PluggableAuthService import (
                    MultiPlugins,
                )

                preSetupMultiPlugins = MultiPlugins[:]

                # Allow subclass to load ZCML and products
                self.setUpZope(portal.getPhysicalRoot(), configurationContext)

                # Snapshot Dexterity schemas
                self.snapshotGeneratedSchemas()

                # Allow subclass to configure a persistent fixture
                setSite(portal)
                self.setUpPloneSite(portal)
                setSite(None)

            # Keep track of PAS plugins that were added during setup
            self.snapshotMultiPlugins(preSetupMultiPlugins)
        except Exception:
            del self["configurationContext"]
            self["zodbDB"].close()
            del self["zodbDB"]
            raise

    def tearDown(self):
        with zope.zopeApp() as app:
            portal = app[PLONE_SITE_ID]
            setHooks()
            setSite(portal)

            # Allow subclass to tear down persistent fixture
            self.tearDownPloneSite(portal)

            setSite(None)

            # Reset Dexterity schemas
            self.tearDownGeneratedSchemas()

            # Make sure zope.security checkers can be set up and torn down
            # reliably

            security.popCheckers()

            # Pop the component registry, thus removing component
            # architecture registrations
            popGlobalRegistry(portal)

            # Remove PAS plugins
            self.tearDownMultiPlugins()

            # Allow subclass to tear down products
            self.tearDownZope(app)

        # Zap the configuration context
        del self["configurationContext"]

        # Pop the demo storage, thus restoring the database to the
        # previous state
        self["zodbDB"].close()
        del self["zodbDB"]

    # Helpers
    def applyProfile(
        self,
        portal,
        profileName,
        purge_old=None,
        ignore_dependencies=False,
        archive=None,
        blacklisted_steps=None,
    ):
        return applyProfile(
            portal,
            profileName,
            purge_old,
            ignore_dependencies,
            archive,
            blacklisted_steps,
        )

    def loadZCML(self, name="configure.zcml", **kw):
        kw.setdefault("context", self["configurationContext"])
        return xmlconfig.file(name, **kw)

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

    def snapshotGeneratedSchemas(self):
        """Save a snapshot of the plone.dexterity.schema.generated module"""
        from plone.dexterity.schema import generated

        self._generatedSchemas = generated.__dict__.copy()
        todelete = []
        for k in generated.__dict__:
            if not k.startswith("_"):
                todelete.append(k)
        for k in todelete:
            del generated.__dict__[k]

    def tearDownGeneratedSchemas(self):
        """Reset plone.dexterity.schema.generated to its previous state"""
        from plone.dexterity.schema import generated

        generated.__dict__.clear()
        generated.__dict__.update(self._generatedSchemas)


class PloneWithPackageLayer(PloneSandboxLayer):
    def __init__(
        self,
        bases=None,
        name=None,
        module=None,
        zcml_filename=None,
        zcml_package=None,
        gs_profile_id=None,
        additional_z2_products=(),
    ):
        super().__init__(bases, name, module)
        self.zcml_filename = zcml_filename
        self.zcml_package = zcml_package
        self.gs_profile_id = gs_profile_id
        self.additional_z2_products = additional_z2_products

    def setUpZope(self, app, configurationContext):
        """Set up Zope.

        Only load ZCML files.
        """
        self.setUpZCMLFiles()
        for z2Product in self.additional_z2_products:
            zope.installProduct(app, z2Product)

    def setUpZCMLFiles(self):
        """Load default ZCML.

        Can be overridden to load more ZCML.
        """
        if self.zcml_filename is None:
            raise ValueError("ZCML file name has not been provided.")
        if self.zcml_package is None:
            raise ValueError(
                "The package that contains the ZCML file " "has not been provided."
            )
        self.loadZCML(self.zcml_filename, package=self.zcml_package)

    def setUpPloneSite(self, portal):
        """Set up the Plone site.

        Only install GenericSetup profiles
        """
        self.applyProfiles(portal)

    def applyProfiles(self, portal):
        """Install default profile.

        Can be overridden to install more profiles.
        """
        if self.gs_profile_id is not None:
            self.applyProfile(portal, self.gs_profile_id)
