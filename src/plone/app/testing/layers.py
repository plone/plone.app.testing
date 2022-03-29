# -*- coding: utf-8 -*-
# Layers setting up fixtures with a Plone site. Also importable from
# plone.app.testing directly

from Acquisition import aq_base
from plone.app.testing.interfaces import DEFAULT_LANGUAGE
from plone.app.testing.interfaces import PLONE_SITE_ID
from plone.app.testing.interfaces import PLONE_SITE_TITLE
from plone.app.testing.interfaces import SITE_OWNER_NAME
from plone.app.testing.interfaces import SITE_OWNER_PASSWORD
from plone.app.testing.interfaces import TEST_USER_ID
from plone.app.testing.interfaces import TEST_USER_NAME
from plone.app.testing.interfaces import TEST_USER_PASSWORD
from plone.app.testing.interfaces import TEST_USER_ROLES
from plone.app.testing.utils import MockMailHost
from plone.registry.interfaces import IRegistry
from plone.testing import Layer
from plone.testing import zca
from plone.testing import zodb
from plone.testing import zope
from plone.testing import zserver
from Products.MailHost.interfaces import IMailHost
from zope.component import getSiteManager
from zope.component import getUtility
from zope.component.hooks import setSite
from zope.event import notify
from zope.traversing.interfaces import BeforeTraverseEvent

import six
import transaction


class PloneFixture(Layer):
    """This layer sets up a basic Plone site, with:

    * No content
    * No default workflow
    * One user, as found in the constant ``TEST_USER_ID``, with login name
      ``TEST_USER_NAME``, the password ``TEST_USER_PASSWORD``, and a single
      role, ``Member``.
    """

    defaultBases = (zope.STARTUP,)

    # Products that will be installed, plus options
    products = (
        ('Products.GenericSetup', {'loadZCML': True}, ),
        ('Products.DCWorkflow', {'loadZCML': True}, ),
        ('Products.ZCTextIndex', {'loadZCML': True}, ),
        ('Products.DateRecurringIndex', {'loadZCML': False}, ),
        ('Products.PageTemplates', {'loadZCML': True}, ),
        ('Products.CMFUid', {'loadZCML': True}, ),
        ('Products.CMFCore', {'loadZCML': True}, ),
        ('Products.PluggableAuthService', {'loadZCML': True}, ),
        ('Products.PluginRegistry', {'loadZCML': True}, ),
        ('Products.PlonePAS', {'loadZCML': True}, ),
        ('Products.CMFDynamicViewFTI', {'loadZCML': True}, ),
        ('Products.CMFPlacefulWorkflow', {'loadZCML': True}, ),
        ('Products.MimetypesRegistry', {'loadZCML': True}, ),
        ('Products.PortalTransforms', {'loadZCML': True}, ),
        ('Products.ExtendedPathIndex', {'loadZCML': True}, ),
        ('Products.SiteAccess', {'loadZCML': False}, ),
        ('Products.CMFEditions', {'loadZCML': True}, ),
        ('Products.CMFDiffTool', {'loadZCML': True}, ),
        ('plone.i18n', {'loadZCML': True, 'install': False}, ),
        ('plonetheme.barceloneta', {'loadZCML': True, 'install': False}, ),
        ('Products.CMFPlone', {'loadZCML': True}, ),
        ('Products.PythonScripts', {'loadZCML': False}, ),
    )
    if six.PY2:
        products += (
            ('Products.ExternalEditor', {'loadZCML': True}, ),
        )

        try:
            # Since gopipindex moved to plone.folder only with Archetypes
            import plone.app.folder
            # Prevent trying to load plone.app.folder if it is a module alias
            if hasattr(plone.app.folder, "__file__"):
                products += (
                    ('plone.app.folder', {'loadZCML': True}, ),
                )
        except ImportError:
            pass

    # Extension profiles to be installed with site setup
    extensionProfiles = (
        'plonetheme.barceloneta:default',
    )

    # Layer lifecycle

    def setUp(self):

        # Stack a new DemoStorage on top of the one from zope.STARTUP.
        self['zodbDB'] = zodb.stackDemoStorage(
            self.get('zodbDB'),
            name='PloneFixture'
        )

        self.setUpZCML()

        # Set up products and the default content
        with zope.zopeApp() as app:
            self.setUpProducts(app)
            self.setUpDefaultContent(app)
            # If there is no savepoint most tests fail with a PosKeyError
            # See https://github.com/plone/Products.CMFPlone/issues/3467
            transaction.savepoint(optimistic=True)

    def tearDown(self):

        # Tear down products
        with zope.zopeApp() as app:
            # note: content tear-down happens by squashing the ZODB
            self.tearDownProducts(app)

        self.tearDownZCML()

        # Zap the stacked ZODB
        self['zodbDB'].close()
        del self['zodbDB']

    def setUpZCML(self):
        """Stack a new global registry and load ZCML configuration of Plone
        and the core set of add-on products into it. Also set the
        ``disable-autoinclude`` ZCML feature so that Plone does not attempt to
        auto-load ZCML using ``z3c.autoinclude``.
        """

        # Create a new global registry
        zca.pushGlobalRegistry()

        from zope.configuration import xmlconfig
        self['configurationContext'] = context = zca.stackConfigurationContext(
            self.get('configurationContext')
        )

        # Turn off z3c.autoinclude

        xmlconfig.string("""\
<configure xmlns="http://namespaces.zope.org/zope"
           xmlns:meta="http://namespaces.zope.org/meta">
    <meta:provides feature="disable-autoinclude" />
</configure>
""", context=context)

        # Load dependent products's ZCML - Plone doesn't specify dependencies
        # on Products.* packages fully

        from zope.dottedname.resolve import resolve

        def loadAll(filename):
            for p, config in self.products:
                if not config['loadZCML']:
                    continue
                try:
                    package = resolve(p)
                except ImportError:
                    continue
                try:
                    xmlconfig.file(filename, package, context=context)
                except IOError:
                    pass

        loadAll('meta.zcml')
        loadAll('configure.zcml')
        loadAll('overrides.zcml')

    def tearDownZCML(self):
        """Pop the global component registry stack, effectively unregistering
        all global components registered during layer setup.
        """
        # Pop the global registry
        zca.popGlobalRegistry()

        # Zap the stacked configuration context
        del self['configurationContext']

    def setUpProducts(self, app):
        """Install all old-style products listed in the the ``products`` tuple
        of this class.
        """

        for p, config in self.products:
            if config.get('install', True):
                zope.installProduct(app, p)

    def tearDownProducts(self, app):
        """Uninstall all old-style products listed in the the ``products``
        tuple of this class.
        """
        for p, config in reversed(self.products):
            if config.get('install', True):
                zope.uninstallProduct(app, p)

        # Clean up Wicked turds
        # XXX: This may tear down too much state
        try:
            from wicked.fieldevent import meta
            meta.cleanUp()
        except ImportError:
            pass

    def setUpDefaultContent(self, app):
        """Add the site owner user to the root user folder and log in as that
        user. Create the Plone site, installing the extension profiles listed
        in the ``extensionProfiles`` layer class variable. Create the test
        user inside the site, and disable the default workflow.

        Note: There is no explicit tear-down of this setup operation, because
        all persistent changes are torn down when the stacked ZODB
        ``DemoStorage`` is popped.
        """

        # Create the owner user and "log in" so that the site object gets
        # the right ownership information
        app['acl_users'].userFolderAddUser(
            SITE_OWNER_NAME,
            SITE_OWNER_PASSWORD,
            ['Manager'],
            []
        )

        zope.login(app['acl_users'], SITE_OWNER_NAME)

        # Create the site with the default set of extension profiles
        from Products.CMFPlone.factory import addPloneSite
        addPloneSite(
            app,
            PLONE_SITE_ID,
            title=PLONE_SITE_TITLE,
            setup_content=False,
            default_language=DEFAULT_LANGUAGE,
            extension_ids=self.extensionProfiles,
        )

        # Turn off default workflow
        app[PLONE_SITE_ID]['portal_workflow'].setDefaultChain('')

        # Create the test user. (Plone)PAS does not have an API to create a
        # user with different userid and login name, so we call the plugin
        # directly.
        pas = app[PLONE_SITE_ID]['acl_users']
        pas.source_users.addUser(
            TEST_USER_ID,
            TEST_USER_NAME,
            TEST_USER_PASSWORD
        )
        for role in TEST_USER_ROLES:
            pas.portal_role_manager.doAssignRoleToPrincipal(TEST_USER_ID, role)

        # Log out again
        zope.logout()


# Plone fixture layer instance. Should not be used on its own, but as a base
# for other layers.
PLONE_FIXTURE = PloneFixture()


class PloneZServerFixture(PloneFixture):
    """PloneFixture using ZServer if you really have to.

    e. g. to use the FTP server.

    """

    defaultBases = (zserver.STARTUP,)

    def setUp(self):

        # Stack a new DemoStorage on top of the one from zserver.STARTUP.
        self['zodbDB'] = zodb.stackDemoStorage(
            self.get('zodbDB'),
            name='PloneZServerFixture'
        )

        self.setUpZCML()

        # Set up products and the default content
        with zserver.zopeApp() as app:
            self.setUpProducts(app)
            self.setUpDefaultContent(app)

    def tearDown(self):

        # Tear down products
        with zserver.zopeApp() as app:
            # note: content tear-down happens by squashing the ZODB
            self.tearDownProducts(app)

        self.tearDownZCML()

        # Zap the stacked ZODB
        self['zodbDB'].close()
        del self['zodbDB']


PLONE_ZSERVER_FIXTURE = PloneZServerFixture()


class PloneTestLifecycle(object):
    """Mixin class for Plone test lifecycle. This exposes the ``portal``
    resource and resets the environment between each test.

    This class is used as a mixing for the IntegrationTesting and
    FunctionalTesting classes below, which also mix in the z2 versions of
    the same.
    """

    defaultBases = (PLONE_FIXTURE,)

    def testSetUp(self):
        super(PloneTestLifecycle, self).testSetUp()

        self['portal'] = portal = self['app'][PLONE_SITE_ID]
        self.setUpEnvironment(portal)

    def testTearDown(self):
        self.tearDownEnvironment(self['portal'])
        del self['portal']

        super(PloneTestLifecycle, self).testTearDown()

    def setUpEnvironment(self, portal):
        """Set up the local component site, reset skin data and log in as
        the test user.
        """

        # Set up the local site manager
        setSite(portal)

        # Reset skin data
        portal.clearCurrentSkin()
        portal.setupCurrentSkin(portal.REQUEST)
        notify(BeforeTraverseEvent(portal, portal.REQUEST))

        # Pseudo-login as the test user
        from plone.app.testing import helpers
        helpers.login(portal, TEST_USER_NAME)

    def tearDownEnvironment(self, portal):
        """Log out, invalidate standard RAM caches, and unset the local
        component site to clean up after tests.
        """

        # Clear the security manager
        from plone.app.testing import helpers
        helpers.logout()

        # Clear any cached data using plone.memoize's RAM caches
        from plone.memoize.ram import global_cache
        global_cache.invalidateAll()

        from zope.component import queryUtility
        from plone.memoize.ram import IRAMCache
        cache = queryUtility(IRAMCache)
        if cache and getattr(cache, '_cacheId', None):
            cache.invalidateAll()

        # Unset the local component site
        setSite(None)


class PloneZServerTestLifecycle(PloneTestLifecycle):
    """PloneTestLifecycle if you have to use ZServer."""

    defaultBases = (PLONE_ZSERVER_FIXTURE,)


class MockMailHostLayer(Layer):
    """Layer for setting up a MockMailHost to store all sent messages as
    strings into a list at portal.MailHost.messages
    """
    defaultBases = (PLONE_FIXTURE,)

    def testSetUp(self):
        with zope.zopeApp() as app:
            portal = app[PLONE_SITE_ID]
            registry = getUtility(IRegistry, context=portal)

            if not registry["plone.email_from_address"]:
                portal._original_email_address = registry["plone.email_from_address"]  # noqa: E501
                registry["plone.email_from_address"] = "noreply@example.com"

            if not registry["plone.email_from_name"]:
                portal._original_email_name = registry["plone.email_from_name"]
                registry["plone.email_from_name"] = u"Plone site"

            portal._original_MailHost = portal.MailHost
            portal.MailHost = mailhost = MockMailHost('MailHost')

            sm = getSiteManager(context=portal)
            sm.unregisterUtility(provided=IMailHost)
            sm.registerUtility(mailhost, provided=IMailHost)

    def testTearDown(self):

        with zope.zopeApp() as app:
            portal = app[PLONE_SITE_ID]
            registry = getUtility(IRegistry, context=portal)

            portal.MailHost = portal._original_MailHost

            sm = getSiteManager(context=portal)
            sm.unregisterUtility(provided=IMailHost)
            sm.registerUtility(aq_base(portal.MailHost), provided=IMailHost)

            if hasattr(portal, "_original_email_name"):
                registry["plone.email_from_name"] = portal._original_email_name
                delattr(portal, "_original_email_name")

            if hasattr(portal, "_original_email_address"):
                registry["plone.email_from_address"] = portal._original_email_address  # noqa: E501
                delattr(portal, "_original_email_address")

            delattr(portal, "_original_MailHost")


MOCK_MAILHOST_FIXTURE = MockMailHostLayer()


class IntegrationTesting(PloneTestLifecycle, zope.IntegrationTesting):
    """Plone version of the integration testing layer
    """


class FunctionalTesting(PloneTestLifecycle, zope.FunctionalTesting):
    """Plone version of the functional testing layer
    """


class ZServerFunctionalTesting(
        PloneZServerTestLifecycle, zserver.FunctionalTesting):
    """Plone version of the functional testing layer using ZServer.
    """

#
# Layer instances
#
# Note: PLONE_FIXTURE is defined above


PLONE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_FIXTURE, ),
    name='Plone:Integration'
)

PLONE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_FIXTURE, ),
    name='Plone:Functional'
)

PLONE_WSGISERVER = PLONE_ZSERVER = FunctionalTesting(
    bases=(PLONE_FIXTURE, zope.WSGI_SERVER_FIXTURE),
    name='Plone:WSGIServer'
)

PLONE_FTP_SERVER = ZServerFunctionalTesting(
    bases=(PLONE_ZSERVER_FIXTURE, zserver.FTP_SERVER_FIXTURE),
    name='Plone:FTPServer'
)
