# Layers setting up fixtures with a Plone site. Also importable from
# plone.app.testing directly

from plone.testing import Layer
from plone.testing import zodb, zca, z2

from plone.app.testing.interfaces import (
        PLONE_SITE_ID,
        PLONE_SITE_TITLE,
        DEFAULT_LANGUAGE,
        
        TEST_USER_NAME,
        TEST_USER_PASSWORD,
        TEST_USER_ROLES,
        
        SITE_OWNER_NAME,
        SITE_OWNER_PASSWORD
    )

class PloneSite(Layer):
    """This layer sets up a basic Plone site, with:
    
    * No content
    * No default workflow
    * One user, as found in the constant ``TEST_USER_NAME``, with the password
      ``TEST_USER_PASSWORD``, and a single role, ``Member``.
    * A resource ``portal``, which is the portal itself
    """
    
    # Note: We don't set the default bases, since we have two "equal" versions
    # in INTEGRATION_TESTING and FUNCTIONAL_TESTING, both instantiated below
    defaultBases = ()
    
    def __init__(self, bases=None, name=None, module=None):
        if not bases:
            raise ValueError("PloneSite layer must be instantiated with explicit bases")
        super(PloneSite, self).__init__(bases, name, module)
    
    # Products that will be installed, plus options
    products = (
            ('Products.GenericSetup'                , {'loadZCML': True},),
            ('Products.DCWorkflow'                  , {'loadZCML': True}, ),
            ('Products.ZCTextIndex'                 , {'loadZCML': True}, ),
                                                    
            ('Products.CMFActionIcons'              , {'loadZCML': True}, ),
            ('Products.CMFUid'                      , {'loadZCML': True}, ),
            ('Products.CMFCalendar'                 , {'loadZCML': True}, ),
                                                    
            ('Products.CMFCore'                     , {'loadZCML': True},),
            ('Products.CMFDefault'                  , {'loadZCML': True}, ),
                                                    
            ('Products.PluggableAuthService'        , {'loadZCML': True}, ),
            ('Products.PluginRegistry'              , {'loadZCML': True}, ),
            ('Products.PlonePAS'                    , {'loadZCML': True}, ),
                                                    
            ('Products.CMFQuickInstallerTool'       , {'loadZCML': True}, ),
            ('Products.CMFFormController'           , {'loadZCML': True}, ),
            ('Products.CMFDynamicViewFTI'           , {'loadZCML': True}, ),
                                                    
            ('Products.Archetypes'                  , {'loadZCML': True}, ),
            ('Products.MimetypesRegistry'           , {'loadZCML': True}, ),
            ('Products.PortalTransforms'            , {'loadZCML': True}, ),
                                                    
            ('Products.ATContentTypes'              , {'loadZCML': True}, ),
            ('Products.ATReferenceBrowserWidget'    , {'loadZCML': True}, ),
                                                    
            ('Products.ExternalEditor'              , {'loadZCML': True}, ),
            ('Products.ExtendedPathIndex'           , {'loadZCML': True}, ),
            ('Products.ResourceRegistries'          , {'loadZCML': True}, ),
            ('Products.SecureMailHost'              , {'loadZCML': True}, ),
                                                    
            ('Products.PasswordResetTool'           , {'loadZCML': True}, ),
                                                    
            ('Products.CMFPlacefulWorkflow'         , {'loadZCML': True}, ),
            ('Products.kupu'                        , {'loadZCML': True}, ),
            ('Products.TinyMCE'                     , {'loadZCML': True}, ),
                                                    
            ('Products.CMFEditions'                 , {'loadZCML': True}, ),
            ('Products.CMFDiffTool'                 , {'loadZCML': True}, ),
            
            ('Products.PlacelessTranslationService' , {'loadZCML': True}, ),
            ('Products.PloneLanguageTool'           , {'loadZCML': True}, ),
                                                    
            ('plonetheme.classic'                   , {'loadZCML': True}, ),
            ('plonetheme.sunburst'                  , {'loadZCML': True}, ),
                                                    
            ('Products.CMFPlone'                    , {'loadZCML': True}, ),
        )
    
    # Extension profiles to be installed with site setup
    extensionProfiles = (
            'plonetheme.sunburst:default',
        )
    
    # Layer lifecycle
    
    def setUp(self):
        
        # Stack a new DemoStorage on top of the one from z2.STARTUP.
        self['zodbDB'] = zodb.stackDemoStorage(self.get('zodbDB'), name='PloneSite')
        
        # Keep track of the GenericSetup registries so that we can snapshot
        # the changes
        from Products.GenericSetup.registry import _profile_registry
        from Products.GenericSetup.registry import _import_step_registry
        from Products.GenericSetup.registry import _export_step_registry
        
        preSetupProfiles    = list(_profile_registry._profile_ids)
        preSetupImportSteps = list(_import_step_registry.listSteps())
        preSetupExportSteps = list(_export_step_registry.listSteps())
        
        self.setUpZCML()
        
        # Set up products and the default content
        with z2.zopeApp() as app:
            self.setUpProducts(app)
            self.setUpDefaultContent(app)
        
        # Record the changes to the GenericSetup registries
        self.snapshotProfileRegistry(preSetupProfiles, preSetupImportSteps, preSetupExportSteps)
    
    def tearDown(self):
        
        # Tear down products
        with z2.zopeApp() as app:
            # note: content tear-down happens by squashing the ZODB
            self.tearDownProducts(app)
        
        self.tearDownZCML()
        self.tearDownProfileRegistry()
        
        # Zap the stacked ZODB
        self['zodbDB'].close()
        del self['zodbDB']
    
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
    
    def setUpZCML(self):
        """Stack a new global registry and load ZCML configuration of Plone
        and the core set of add-on products into it. Also set the
        ``disable-autoinclude`` ZCML feature so that Plone does not attempt to
        auto-load ZCML using ``z3c.autoinclude``.
        """
        
        # Create a new global registry
        zca.pushGlobalRegistry()
        
        from zope.configuration import xmlconfig
        self['configurationContext'] = context = zca.stackConfigurationContext(self.get('configurationContext'))
        
        # Turn off z3c.autoinclude
        
        xmlconfig.string("""\
<configure xmlns="http://namespaces.zope.org/zope" xmlns:meta="http://namespaces.zope.org/meta">
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
            z2.installProduct(app, p)
    
    def tearDownProducts(self, app):
        """Uninstall all old-style products listed in the the ``products``
        tuple of this class.
        """
        for p, config in reversed(self.products):
            z2.uninstallProduct(app, p)
    
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
        
        z2.login(app['acl_users'], SITE_OWNER_NAME)
        
        # Create the site with the default set of extension profiles
        from Products.CMFPlone.factory import addPloneSite
        addPloneSite(app, PLONE_SITE_ID,
                title=PLONE_SITE_TITLE,
                setup_content=False,
                default_language=DEFAULT_LANGUAGE,
                extension_ids=self.extensionProfiles,
            )
        
        # Turn off default workflow
        app[PLONE_SITE_ID]['portal_workflow'].setDefaultChain('')
        
        # Create the test user
        app[PLONE_SITE_ID]['acl_users'].userFolderAddUser(
                TEST_USER_NAME,
                TEST_USER_PASSWORD,
                TEST_USER_ROLES,
                []
            )
        
        # Log out again
        z2.logout()
    
    # Test lifecycle
    
    def testSetUp(self):
        self['portal'] = portal = self['app'][PLONE_SITE_ID]
        self.setUpEnvironment(portal)
    
    def testTearDown(self):
        self.tearDownEnvironment(self['portal'])
        del self['portal']
    
    def setUpEnvironment(self, portal):
        """Set up the local component site, reset skin data and log in as
        the test user.
        """
        
        # Set up the local site manager
        from zope.site.hooks import setSite
        setSite(portal)
        
        # Reset skin data
        portal.clearCurrentSkin()
        portal.setupCurrentSkin(portal.REQUEST)
        
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
        if cache is not None:
            cache.invalidateAll()
        
        # Unset the local component site
        from zope.site.hooks import setSite
        setSite(None)
    

# Layer instances

PLONE_INTEGRATION_TESTING = PloneSite(bases=(z2.INTEGRATION_TESTING,), name='PloneSite:Integration')
PLONE_FUNCTIONAL_TESTING  = PloneSite(bases=(z2.FUNCTIONAL_TESTING,), name='PloneSite:Functional')
PLONE_ZSERVER             = z2.ZServer(bases=(PLONE_FUNCTIONAL_TESTING,), name='PloneZServer')
PLONE_FTP_SERVER          = z2.FTPServer(bases=(PLONE_FUNCTIONAL_TESTING,), name='PloneFTPServer')
