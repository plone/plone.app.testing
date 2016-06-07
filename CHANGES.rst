Changelog
=========

5.0.2 (2016-06-07)
------------------

Fixes:

- Do not use install Products.SecureMailHost in the PloneFixture if it isn't available
  [vangheem]


5.0.1 (2016-02-26)
------------------

Fixes:

- Replace deprecated ``zope.site.hooks`` import with ``zope.component.hooks``.
  [thet]


5.0.0 (2016-02-20)
------------------

New:

- Add a MOCK_MAILHOST_FIXTURE fixture that integration and functional tests layers can depend on.
  This allows to easily check how mails are sent from Plone.
  [gforcada]

Fixes:

- Fix ``layers.rst`` doctest to be compatible with older and newer zope.testrunner layer ordering.
  [thet]

- Depend on ``zope.testrunner`` and fix deprecated usage of ``zope.testing.testrunner``.
  [thet]

- Cleanup code, flake8, sort imports, etc.
  [gforcada]

- Fix RAM cache error with bbb.PloneTestCase.
  [ebrehault]


5.0b6 (2015-08-22)
------------------

- No need for unittest2.
  [gforcada]


5.0b5 (2015-07-18)
------------------

- Do not install CMFDefault.
  [tomgross]

- Document PloneWithPackageLayer.
  [gotcha]


5.0b4 (2015-05-04)
------------------

- Do not install CMFFormController.
  [timo]

- Do not install CMFDefault
  [tomgross]

5.0b3 (2015-03-26)
------------------

- Remove PloneLanguageTool from PloneFixture.
  [timo]


5.0b2 (2015-03-13)
------------------

- remove test of applying an extension profile, we don't have a good one to
  test now.
  [davidagli]

- fix test, plone.app.theming does not get recorded as installed .
  [davisagli]

- fix: ``Products.CMFPlone`` needs the ``gopip`` index from
  ``plone.app.folder``. So latter has to be initialized before CMFPlones
  profile is applied (which installs the index to catalog). At the moment
  CMFPlone therefore registers the index itself, but plone.app.folder
  registers it too, which resulted in plone/Products.CMFPlone#313
  "GopipIndex registered twice" In tests the registration does not succedd,
  because plone.app.folder was never initialized as z2 products. In order to
  remove the misleading regisatration from CMFPlone we must take care that the
  index is available, which is achieved with this change. Also minor pep8
  optimizations in the file touched.
  [jensens]

- create memberfolder, if it is not there for testing.
  [tomgross]


5.0b1 (2014-10-23)
------------------

- Allow applyProfile to skip steps and all other options supported by
  runAllImportStepsFromProfile of portal_setup-tool.
  [pbauer, tomgross]


5.0a2 (2014-04-19)
------------------

- Install Products.DateRecurringIndex for the PLONE_FIXTURE Layer.
  [thet]


5.0a1 (2014-02-22)
------------------

- Add 'ROBOT_TEST_LEVEL' to interfaces, so other packages can import it. This
  makes things easier if we decide to change the value.
  [timo]

- Replace deprecated test assert statements.
  [timo]

- plonetheme.classic no longer ships with Plone, don't use it for
  testing.
  [esteele]

- Clean up the zodbDB and configurationContext resources if there
  is an error during the PloneSandboxLayer setUp.
  [davisagli]

- Make PLONE_FIXTURE not install a content type system.
  Packages that need content types to run their tests should
  pick the appropriate fixture from plone.app.contenttypes
  or Products.ATContentTypes.
  [davisagli]

- Pin [robot] extra to ``robotsuite>=1.4.0``.
  [saily]

- Fix wrong spelling of ``reinstallProducts`` method in quickInstallProduct.
  [saily]

- Sync bbb PloneTestCase class with original one.
  [tomgross]


4.2.2 (2013-02-09)
------------------

- Add [robot] extras for requiring dependnecies for Robot Framework
  tests with Selenium2Library
  [datakurre]

- Install PythonScripts as zope product
  [mikejmets]


4.2.1 (2012-12-15)
------------------

- Allow testing with non standard port. Allows running multiple test suites
  in parallel.
  [do3cc]

- Documentation updates.
  [moo]


4.2 (2012-04-15)
----------------

- Branch as 4.2 as the plone.app.collection addition breaks backwards
  compatibility.
  [esteele]

- Fixed spurious failure in our own tests by using a longer timeout.
  [maurits]

- plone.app.collection added to PloneFixture.
  [timo]


4.0.2 (2011-08-31)
------------------

- Load ZCML before installing Zope products in ``PloneWithPackageLayer``;
  it enables package registration.
  [gotcha]


4.0.1 (2011-07-14)
------------------

- Add ``additional_z2_products`` parameter to ``PloneWithPackageLayer``
  helper class to install additional Zope 2 products.
  [jfroche]


4.0 - 2011-05-13
------------------

- 4.0 Final release.
  [esteele]

- Add MANIFEST.in.
  [WouterVH]


4.0a6 - 2011-04-06
------------------

- Added helper functions for selenium layer. (Copied from SeleniumTestCase
  within Products.CMFPlone/Products/CMFPlone/tests/selenium/base.py)
  [emanlove]

- Rework layer setup of SeleniumLayer so that z2.ZSERVER_FIXTURE is a
  default_base.
  [esteele]

- Convert the passed-in selenium webdriver name to lowercase before doing a
  module lookup.
  [esteele]

- Moved selenium start up and tear down to testSetUp and testTearDown,
  respectively.  This was done to help further isolate individual tests.
  For example, logging in under one test would require either logging out
  or shutting down the browser, which is what the selenium_layer will now
  do under testTearDown, in order to have a "clean" state within the next
  test.
  [emanlove]

- Corrected module path for the various selenium webdrivers using
  selenium 2.0b2.
  [emanlove]


4.0a5 - 2011-03-02
------------------

- Use the new ``plone.testing.security`` module to ensure isolation of
  security checkers when setting up and tearing down layers based on the
  ``PloneSandboxLayer`` helper base class. This would cause problems when
  running multiple test suites in the same test run, in particular if one of
  those suites were setting up ZCML that used ``five.grok``.
  [optilude]


4.0a4 - 2011-01-11
------------------

- Automatically tear down PAS registrations via snapshotting when using
  ``PloneSandboxLayer``. It's too difficult to do this manually when you
  consider that plugins may be registered in ZCML via transitive dependencies.
  There should be no backwards compatibility concern - using
  ``tearDownMultiPlugin()`` is still supported, and it's generally safe to
  call it once.
  [optilude]

- Try to make sure ``tearDownMultiPlugin()`` and the generic PAS plugin
  cleanup handler do not interfere with the cleanup handler from the PAS
  ZCML directive.
  [optilude]

- Do not install ``Products.kupu`` or ``Products.CMFPlacefulWorkflow``.
  [elro]

- Depend on ``Products.CMFPlone`` instead of ``Plone``.
  [elro]


4.0a3 - 2010-12-14
------------------

- Allow top-level import of PloneTestLifecycle.
  [stefan]

- Added a warning not to use 'default' Firefox profile for selenium tests.
  [zupo]

- Fixed distribution dependency declarations.
  [hannosch]

- Correct license to GPL version 2 only.
  [hannosch]

- Make some module imports helper methods on the already policy-heavy
  helper class per optilude's suggestion.
  [rossp]

- Add a layer and test case for running selenium tests.
  [rossp]

- Give the default test user differing user id and login name. This helps reveal
  problems with userid vs login name errors, an overly common error.
  [wichert]


1.0a2 - 2010-09-05
------------------

- Make sure plone.app.imaging is installed properly during layer setup.
  [optilude]


1.0a1 - 2010-08-01
------------------

- Initial release
