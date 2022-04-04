Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

7.0.0a2 (2022-04-04)
--------------------

Bug fixes:


- Add savepoint after creating the portal in PloneFixture.
  Fixes `issue 3467 <https://github.com/plone/Products.CMFPlone/issues/3467>`_.
  [pbauer] (#76)


7.0.0a1 (2022-03-23)
--------------------

Breaking changes:


- Plone 6 only. (#75)


New features:


- remove CMFFormController
  [petschki] (#75)


6.1.9 (2021-09-01)
------------------

Bug fixes:


- Fixed test that failed for dexterity site root.
  [jaroel, ale-rt] (#60)


6.1.8 (2020-11-11)
------------------

Bug fixes:


- Before trying to load the zcml of plone.app.folder, double check if it is a real package or an alias provided by plone.app.upgrade (#72)


6.1.7 (2020-10-12)
------------------

New features:


- Removed backwards compatibility code for old quickinstaller.
  Current plone.app.testing is only for Plone 5.2+, so this code was no longer used.
  See also `PLIP 1775 <https://github.com/plone/Products.CMFPlone/issues/1775>`_.
  [maurits] (#1775)


6.1.6 (2020-09-26)
------------------

Bug fixes:


- Fixed test failure on Python 3 with Products.MailHost 4.10.
  [maurits] (#3178)


6.1.5 (2020-04-20)
------------------

Bug fixes:


- Minor packaging updates. (#1)


6.1.4 (2020-03-09)
------------------

Bug fixes:


- Fix a test isolation issue that was preventing the MOCK_MAILHOST_FIXTURE to be used in multiple testcases [ale-rt] (#61)
- MockMailHostLayer configures the mail sender setting the appropriate registry records (Fixes #62) (#62)
- Fix tests when using zope.testrunner internals since its version 5.1.
  [jensens] (#68)
- Do not load Products/ZCML of no longer existing Products.ResourceRegistries.
  [jensens] (#69)


6.1.3 (2019-02-16)
------------------

Bug fixes:


- Make plone.app.folder a optional product for PloneFixture in py2 (#59)


6.1.2 (2019-02-13)
------------------

Bug fixes:


- Fixed the travis build checking the Python versions Plone actually supports.
  Also fixed Python versions in setup.py (#57)


6.1.1 (2018-11-05)
------------------

Bug fixes:

- Fix the package manifest that was not including some files
  [ale-rt]


6.1.0 (2018-11-04)
------------------

Breaking changes:

- Require `plone.testing >= 7.0`.

New features:

- Add support for Python 3.5 and 3.6.
  [loechel, ale-rt, icemac, davisagli, pbauer]


6.0.0 (2018-10-05)
------------------

New features:

- Install and load zcml of CMFQuickInstallerTool only when importable.
  [maurits]

- Load negotiator from plone.i18n (PTS removed).
  [jensens, ksuess]

- Add copy of bbb.PloneTestCase.
  For Plone 5.2 the bbb.PloneTestCase will uses Dexterity instead of Archetypes.
  Adding bbb_at.PloneTestCase for them to use allows to keep the AT tests working.
  See https://github.com/plone/plone.app.testing/pull/51
  [pbauer]

Bug fixes:

- Amended the doctests to work with automatical layer port picking from plone.testing.
  [Rotonen]


5.0.8 (2017-10-25)
------------------

Bug fixes:

- Load Products.PageTemplates ZCML.  [tschorr]


5.0.7 (2017-07-03)
------------------

Bug fixes:

- Remove deprecated __of__ calls on BrowserViews
  [MrTango]

- Remove unittest2 dependency
  [kakshay21]


5.0.6 (2016-12-19)
------------------

Bug fixes:

- No longer try to load `Products.SecureMailHost` and its zcml.
  This is not shipped with Plone 5.0 or higher.  [maurits]


5.0.5 (2016-11-19)
------------------

Bug fixes:

- Do not use install Products.PasswordResetTool in the PloneFixture if it isn't available.
  [thet]


5.0.4 (2016-09-23)
------------------

New features:

- Use get_installer instead of portal_quickinstaller when available, for
  Plone 5.1 and higher.  [maurits]

- In PloneSandboxLayer make profile upgrade versions persistent.  This
  way installed profile versions get reset in teardown.  [maurits]


5.0.3 (2016-09-07)
------------------

Bug fixes:

- Load Products.CMFFormController in tests.  It is still used by core
  Plone, also without Archetypes.  This makes the CMFFormController
  tests pass.  [maurits]


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
