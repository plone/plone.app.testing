Plone testing helpers
---------------------

This package contains various test helpers that are useful for writing custom
layers using layers that are based on the ``PLONE_FIXTURE`` layer, and for
writing tests using such layers.

The helpers are all importable from ``plone.app.testing`` directly, or from
their canonical locations at ``plone.app.testing.helpers``.

    >>> from plone.app.testing import helpers

For testing, we need a testrunner

    >>> from zope.testrunner import runner

Let's create a custom fixture layer that exercises these helpers. In this
layer, we will perform the following setup:

1. Stack a new ``DemoStorage`` on top of the one from the base layer. This
   ensures that any persistent changes performed in this layer can be torn
   down completely, simply by popping the demo storage.

2. Stack a new ZCML configuration context. This keeps separate the information
   about which ZCML files were loaded, in case other, independent layers want
   to load those same files after this layer has been torn down.

3. Push a new global component registry. This allows us to register components
   (e.g. by loading ZCML or using the test API from ``zope.component``) and
   tear down those registration easily by popping the component registry.
   We pass the portal so that the local component site manager can be
   configured appropriately.

   *Note:* We obtain the portal from the ``ploneSite()`` context manager,
   which will ensure that the portal is properly set up and commit our changes
   on exiting the ``with`` block.

4. Make some persistent changes, to illustrate how these are torn down when
   we pop the ZODB ``DemoStorage``.

5. Install a product using the ``get_installer`` view.

6. Apply a named extension profile.

On tear-down, we only need to pop the ``DemoStorage`` (to roll back all
persistent changes), the configuration context (to "forget" which files were
loaded and so allow them to be loaded again in other layers), and the stacked
component registry (to roll back all global component registrations). Of
course, if our setup had changed any other global or external state, we would
need to tear that down as well.

    >>> def is_installed(portal, product_name):
    ...     from Products.CMFPlone.utils import get_installer
    ...     qi = get_installer(portal)
    ...     return qi.is_product_installed(product_name)

    >>> from plone.testing import Layer
    >>> from plone.testing import zca, zope, zodb

    >>> from plone.app.testing import PLONE_FIXTURE
    >>> from plone.app.testing import IntegrationTesting

    >>> class HelperDemos(Layer):
    ...     defaultBases = (PLONE_FIXTURE,)
    ...
    ...     def setUp(self):
    ...
    ...         # Push a new database storage so that database changes
    ...         # committed during layer setup can be easily torn down
    ...         self['zodbDB'] = zodb.stackDemoStorage(self.get('zodbDB'), name='HelperDemos')
    ...
    ...         # Push a new configuration context so that it's possible to re-import
    ...         # ZCML files after tear-down
    ...         self['configurationContext'] = zca.stackConfigurationContext(self.get('configurationContext'))
    ...
    ...         with helpers.ploneSite() as portal:
    ...
    ...             # Persist GenericSetup profile upgrade versions for easy rollback.
    ...             helpers.persist_profile_upgrade_versions(portal)
    ...
    ...             # First register dummy default and uninstall profiles for plone.app.testing.
    ...             # We will use this to test that after teardown the installed profile versions get reset.
    ...             # We used to test this with plone.resource, but that is already installed by default,
    ...             # which makes it a pain to test with.
    ...             from Products.GenericSetup.registry import _profile_registry
    ...             from Products.GenericSetup.interfaces import EXTENSION
    ...             # 'profile' points to a path with a metadata.xml so we can have a version.
    ...             _profile_registry.registerProfile('default', u"Testing", u"", "profile", 'plone.app.testing', EXTENSION)
    ...             _profile_registry.registerProfile('uninstall', u"Testing uninstall", u"", "profile", 'plone.app.testing', EXTENSION)
    ...
    ...             # Push a new component registry so that ZCML registrations
    ...             # and other global component registry changes are sandboxed
    ...             helpers.pushGlobalRegistry(portal)
    ...
    ...             # Register some components
    ...             from zope.component import provideUtility
    ...             from zope.interface import Interface
    ...             provideUtility(object(), Interface, name=u"dummy1")
    ...
    ...             # Make some persistent changes
    ...             portal.title = u"New title"
    ...
    ...             # Install a product using the addons control panel
    ...             helpers.quickInstallProduct(portal, 'plone.app.testing')
    ...             assert is_installed(portal, 'plone.app.testing')
    ...
    ...     def tearDown(self):
    ...
    ...         # Pop the component registry, thus removing component
    ...         # architecture registrations
    ...         with helpers.ploneSite() as portal:
    ...             helpers.popGlobalRegistry(portal)
    ...
    ...         # Pop the configuration context
    ...         del self['configurationContext']
    ...
    ...         # Pop the demo storage, thus restoring the database to the
    ...         # previous state
    ...         self['zodbDB'].close()
    ...         del self['zodbDB']

With the layer class defined, we can instantiate a fixture base layer, and
an "end user" layer with test lifecycle management. Here, we will use the
``IntegrationTesting`` layer class from ``plone.app.testing``.

    >>> HELPER_DEMOS_FIXTURE = HelperDemos()
    >>> HELPER_DEMOS_INTEGRATION_TESTING = IntegrationTesting(bases=(HELPER_DEMOS_FIXTURE,), name="HelperDemos:Integration")

Let's now simulate layer setup:

    >>> options = runner.get_options([], [])
    >>> setupLayers = {}
    >>> runner.setup_layer(options, HELPER_DEMOS_INTEGRATION_TESTING, setupLayers)
    Set up plone.testing.zca.LayerCleanup in ... seconds.
      Set up plone.testing.zope.Startup in ... seconds.
      Set up plone.app.testing.layers.PloneFixture in ... seconds.
      Set up...HelperDemos in ... seconds.
      Set up plone.app.testing.layers.HelperDemos:Integration in ... seconds.

We should see the newly registered components and the persistent changes
having taken effect.

    >>> from zope.component import queryUtility
    >>> from zope.interface import Interface
    >>> queryUtility(Interface, name="dummy1")
    <object object at ...>

    >>> with helpers.ploneSite() as portal:
    ...     print(portal.title)
    New title

We should also see our product installation in the add-ons control panel
and the results of the profile having been applied.

    >>> from Products.GenericSetup.tool import UNKNOWN
    >>> with helpers.ploneSite() as portal:
    ...     print(is_installed(portal, 'plone.app.testing'))
    ...     portal.portal_setup.getLastVersionForProfile('plone.app.testing:default') == UNKNOWN
    True
    False

Let's now simulate a test.

    >>> zca.LAYER_CLEANUP.testSetUp()
    >>> zope.STARTUP.testSetUp()
    >>> PLONE_FIXTURE.testSetUp()
    >>> HELPER_DEMOS_FIXTURE.testSetUp()
    >>> HELPER_DEMOS_INTEGRATION_TESTING.testSetUp()

In a test, we can use helpers to simulate login, logging out and changing a
user's roles. These may also be used during layer setup if required, using
the ``ploneSite()`` context manager as shown above.

    >>> from AccessControl import getSecurityManager
    >>> from plone.app.testing import TEST_USER_NAME
    >>> from plone.app.testing import TEST_USER_ID

    >>> portal = HELPER_DEMOS_INTEGRATION_TESTING['portal'] # would normally be self.layer['portal']

    >>> sorted(getSecurityManager().getUser().getRolesInContext(portal))
    ['Authenticated', 'Member']

    >>> getSecurityManager().getUser().getUserName() == TEST_USER_NAME
    True
    >>> getSecurityManager().getUser().getId() == TEST_USER_ID
    True
    >>> sm_repr = repr(getSecurityManager())
    >>> helpers.setRoles(portal, TEST_USER_ID, ['Manager'])
    >>> repr(getSecurityManager()) != sm_repr
    True
    >>> sorted(getSecurityManager().getUser().getRolesInContext(portal))
    ['Authenticated', 'Manager']

    >>> helpers.logout()
    >>> getSecurityManager().getUser()
    <SpecialUser 'Anonymous User'>

    >>> helpers.login(portal, TEST_USER_NAME)
    >>> getSecurityManager().getUser().getUserName() == TEST_USER_NAME
    True

    >>> from OFS.Folder import Folder
    >>> portal._setObject('folder1', Folder('folder1'))
    'folder1'

Let's now tear down the test.

    >>> HELPER_DEMOS_INTEGRATION_TESTING.testTearDown()
    >>> HELPER_DEMOS_FIXTURE.testTearDown()
    >>> PLONE_FIXTURE.testTearDown()
    >>> zope.STARTUP.testTearDown()
    >>> zca.LAYER_CLEANUP.testTearDown()

Our persistent changes from the layer should remain, but those made in a test
should not.

    >>> queryUtility(Interface, name="dummy1")
    <object object at ...>

    >>> with helpers.ploneSite() as portal:
    ...     print(portal.title)
    ...     print(is_installed(portal, 'plone.app.testing'))
    ...     'folder1' in portal.objectIds()
    ...     portal.portal_setup.getLastVersionForProfile('plone.app.testing:default') == UNKNOWN
    New title
    True
    False
    False

We'll now tear down just the ``HELPER_DEMOS_INTEGRATION_TESTING`` layer. At this
point, we should still have a Plone site, but none of the persistent or
component architecture changes from our layer.

    >>> runner.tear_down_unneeded(options, [l for l in setupLayers if l not in (HELPER_DEMOS_INTEGRATION_TESTING, HELPER_DEMOS_FIXTURE,)], setupLayers, [])
    Tear down plone.app.testing.layers.HelperDemos:Integration in ... seconds.
    Tear down...HelperDemos in ... seconds.

    >>> queryUtility(Interface, name="dummy1") is None
    True

    >>> with helpers.ploneSite() as portal:
    ...     print(portal.title)
    ...     print(is_installed(portal, 'plone.app.testing'))
    ...     portal.portal_setup.getLastVersionForProfile('plone.app.testing:default') == UNKNOWN
    Plone site
    False
    True

Let's tear down the rest of the layers too.

    >>> runner.tear_down_unneeded(options, [], setupLayers, [])
    Tear down plone.app.testing.layers.PloneFixture in ... seconds.
    Tear down plone.testing.zope.Startup in ... seconds.
    Tear down plone.testing.zca.LayerCleanup in ... seconds.

Plone sandbox layer helper
--------------------------

The pattern above of setting up a stacked ZODB ``DemoStorage``, configuration
context and global component registry is very common. In fact, there is a
layer base class which helps implement this pattern.

    >>> someGlobal = {}

    >>> class MyLayer(helpers.PloneSandboxLayer):
    ...
    ...     def setUpZope(self, app, configurationContext):
    ...
    ...         # We'd often load ZCML here, using the passed-in
    ...         # configurationContext as the configuration context.
    ...
    ...         # Of course, we can also register some components using the
    ...         # zope.component API directly
    ...         from zope.component import provideUtility
    ...         from zope.interface import Interface
    ...         provideUtility(object(), Interface, name=u"dummy1")
    ...
    ...         # We'll also add some entries to the GenericSetup global
    ...         # registries.
    ...         from Products.GenericSetup.registry import _profile_registry
    ...         from Products.GenericSetup.registry import _import_step_registry
    ...         from Products.GenericSetup.registry import _export_step_registry
    ...         from Products.GenericSetup import upgrade
    ...
    ...         _profile_registry.registerProfile('dummy1', u"My package", u"", ".", 'plone.app.testing')
    ...         _import_step_registry.registerStep('import1', version=1, handler='plone.app.testing.tests.dummy', title=u"Dummy import step", description=u"")
    ...         _export_step_registry.registerStep('export1', handler='plone.app.testing.tests.dummy', title=u"Dummy import step", description=u"")
    ...         upgrade_step = upgrade.UpgradeStep(u'Dummy upgrade step', 'plone.app.testing:default', '1000', '1001', '', 'plone.app.testing.tests.dummy')
    ...         upgrade._registerUpgradeStep(upgrade_step)
    ...
    ...         # And then pretend to register a PAS multi-plugin
    ...         from Products.PluggableAuthService import PluggableAuthService
    ...         PluggableAuthService.registerMultiPlugin("dummy_plugin1")
    ...
    ...         # Finally, this is a good place to load Zope products,
    ...         # using the plone.testing.zope.installProduct() helper.
    ...         # Make some other global changes not stored in the ZODB or
    ...         # the global component registry
    ...         someGlobal['test'] = 1
    ...
    ...     def tearDownZope(self, app):
    ...         # Illustrate tear-down of some global state
    ...         del someGlobal['test']
    ...
    ...     def setUpPloneSite(self, portal):
    ...
    ...         # We can make persistent changes here
    ...         portal.title = u"New title"

    >>> MY_FIXTURE = MyLayer()
    >>> MY_INTEGRATION_TESTING = IntegrationTesting(bases=(MY_FIXTURE,), name="MyLayer:Integration")

Here, we have derived from ``PloneSandboxLayer`` instead of the more usual
``Layer`` base class. This layer implements the sandboxing of the ZODB, global
component registry, and GenericSetup profile and import/export step registries
for us, and delegates to four template methods, all of them optional:

* ``setUpZope()``, called with the Zope app root and the ZCML configuration
  context as arguments. This is a good place to load ZCML, manipulate global
  registries, or install Zope 2-style products using the ``installProduct()``
  helper method.
* ``setUpPloneSite()``, called with the Plone site object as an argument. This
  is a good place to set up persistent aspects of the test fixture, such as
  installing products into Plone using the ``quickInstallProduct`` helper or
  adding default content.
* ``tearDownZope()``, called with the Zope app root as an argument. This is
  a good place to tear down global state and uninstall products using the
  ``uninstallProduct()`` helper. Note that global components (e.g. loaded via
  ZCML) are torn down automatically, as are changes to the global GenericSetup
  registries.
* ``tearDownPloneSite()``, called with the Plone site object as an argument.
  This is not very commonly needed, because persistent changes to the Plone
  site are torn down automatically by popping ZODB ``DemoStorage`` created
  during set-up. However, it is there if you need it.

You may also wish to change the ``defaultBases`` argument. The default is to
use ``PLONE_FIXTURE`` as the single default base layer for the fixture class.

    >>> MY_FIXTURE.__bases__
    (<Layer 'plone.app.testing.layers.PloneFixture'>,)

Let's now simulate layer setup:

    >>> options = runner.get_options([], [])
    >>> setupLayers = {}
    >>> runner.setup_layer(options, MY_INTEGRATION_TESTING, setupLayers)
    Set up plone.testing.zca.LayerCleanup in ... seconds.
    Set up plone.testing.zope.Startup in ... seconds.
    Set up plone.app.testing.layers.PloneFixture in ... seconds.
    Set up...MyLayer in ... seconds.
    Set up plone.app.testing.layers.MyLayer:Integration in ... seconds.

Again, our state should now be available.

    >>> queryUtility(Interface, name="dummy1")
    <object object at ...>

    >>> with helpers.ploneSite() as portal:
    ...     print(portal.title)
    New title

    >>> someGlobal['test']
    1

    >>> from Products.GenericSetup.registry import _profile_registry
    >>> from Products.GenericSetup.registry import _import_step_registry
    >>> from Products.GenericSetup.registry import _export_step_registry
    >>> from Products.GenericSetup.upgrade import _upgrade_registry

    >>> numProfiles = len(_profile_registry.listProfiles())
    >>> 'plone.app.testing:dummy1' in _profile_registry.listProfiles()
    True

    >>> numImportSteps = len(_import_step_registry.listSteps())
    >>> 'import1' in _import_step_registry.listSteps()
    True

    >>> numExportSteps = len(_export_step_registry.listSteps())
    >>> 'export1' in _export_step_registry.listSteps()
    True

    >>> from Products.PluggableAuthService import PluggableAuthService
    >>> 'dummy_plugin1' in PluggableAuthService.MultiPlugins
    True

    >>> numUpgrades = len(_upgrade_registry.keys())
    >>> len(_upgrade_registry.getUpgradeStepsForProfile('plone.app.testing:default'))
    1

We'll now tear down just the ``MY_INTEGRATION_TESTING`` layer. At this
point, we should still have a Plone site, but none of the changes from our
layer.

    >>> runner.tear_down_unneeded(options, [l for l in setupLayers if l not in (MY_INTEGRATION_TESTING, MY_FIXTURE)], setupLayers, [])
    Tear down plone.app.testing.layers.MyLayer:Integration in ... seconds.

    >>> queryUtility(Interface, name="dummy1") is None
    True

    >>> with helpers.ploneSite() as portal:
    ...     print(portal.title)
    Plone site

    >>> 'test' in someGlobal
    False

    >>> len(_profile_registry.listProfiles()) == numProfiles - 1
    True
    >>> 'plone.app.testing:dummy1' in _profile_registry.listProfiles()
    False

    >>> len(_import_step_registry.listSteps()) == numImportSteps - 1
    True
    >>> 'import1' in _import_step_registry.listSteps()
    False

    >>> len(_export_step_registry.listSteps()) == numExportSteps - 1
    True
    >>> 'export1' in _export_step_registry.listSteps()
    False

    >>> len(_upgrade_registry.keys()) == numUpgrades - 1
    True
    >>> len(_upgrade_registry.getUpgradeStepsForProfile('plone.app.testing:default'))
    0

    >>> from Products.PluggableAuthService import PluggableAuthService
    >>> 'dummy_plugin1' in PluggableAuthService.MultiPlugins
    False

Let's tear down the rest of the layers too.

    >>> runner.tear_down_unneeded(options, [], setupLayers, [])
    Tear down plone.app.testing.layers.PloneFixture in ... seconds.
    Tear down plone.testing.zope.Startup in ... seconds.
    Tear down plone.testing.zca.LayerCleanup in ... seconds.

Other helpers
-------------

There are some further helpers that apply only to special cases.

Some product that uses the ``<pas:registerMultiPlugin />`` or the
``registerMultiPlugin()`` API from ``PluggableAuthService`` may leave global
state that needs to be cleaned up. You can use the helper
``tearDownMultiPluginRegistration()`` for this purpose.

Let's simulate registering some plugins:

    >>> from Products.PluggableAuthService import PluggableAuthService
    >>> PluggableAuthService.registerMultiPlugin("dummy_plugin1")
    >>> PluggableAuthService.registerMultiPlugin("dummy_plugin2")

    >>> PluggableAuthService.MultiPlugins
    ['dummy_plugin1', 'dummy_plugin2']

If we register plugins with ZCML, they end up in a clean-up list - let's
simulate that too.

    >>> from Products.PluggableAuthService import zcml
    >>> zcml._mt_regs.append('dummy_plugin1')
    >>> zcml._mt_regs.append('dummy_plugin2')

The tear down helper takes a plugin meta-type as an argument:

    >>> helpers.tearDownMultiPluginRegistration('dummy_plugin1')

    >>> PluggableAuthService.MultiPlugins
    ['dummy_plugin2']

    >>> zcml._mt_regs
    ['dummy_plugin2']

Let's clean up the registry completely.

    >>> helpers.tearDownMultiPluginRegistration('dummy_plugin2')
