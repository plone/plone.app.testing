Changelog
=========

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
