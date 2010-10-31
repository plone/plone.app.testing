Selenium testing layer
----------------------

There is a layer used to set up test fixtures for running Selenium
tests against a Plone site. It is importable from
``plone.app.testing.selenium_layers``.

Note that if using the "-D" pdb debugger testrunner flag for failures
in this test before the layer is torn down, the testrunner process
will not exit even with interrupt. Exit by backgrounding the process
and then kill the backgrouned process.

    >>> from plone.app.testing import selenium_layers as layers

For testing, we need a testrunner

    >>> from zope.testing.testrunner import runner

The ``SELENIUM_PLONE_FUNCTIONAL_TESTING`` layer instantiates the
``FunctionalTesting`` class with one base: ``SELENIUM_FIXTURE``, as
shown above.

    >>> "%s.%s" % (
    ...     layers.SELENIUM_PLONE_FUNCTIONAL_TESTING.__module__,
    ...     layers.SELENIUM_PLONE_FUNCTIONAL_TESTING.__name__,)
    'plone.app.testing.selenium_layers.SeleniumTesting:Functional'

    >>> layers.SELENIUM_PLONE_FUNCTIONAL_TESTING.__bases__
    (<Layer 'plone.app.testing.selenium_layers.SeleniumLayer'>, <Layer 'plone.testing.z2.ZServer'>, <Layer 'plone.app.testing.layers.PloneFixture'>)

    >>> options = runner.get_options([], [])
    >>> setupLayers = {}
    >>> runner.setup_layer(
    ...     options, layers.SELENIUM_PLONE_FUNCTIONAL_TESTING, setupLayers)
    Set up plone.app.testing.selenium_layers.SeleniumLayer in ... seconds.
    Set up plone.testing.zca.LayerCleanup in ... seconds.
    Set up plone.testing.z2.Startup in ... seconds.
    Set up plone.app.testing.layers.PloneFixture in ... seconds.
    Set up plone.app.testing.selenium_layers.SeleniumTesting:Functional in ... seconds.

After layer setup, the resources ``host`` and ``port`` are available, and
indicate where Zope is running.

    >>> host = layers.SELENIUM_PLONE_FUNCTIONAL_TESTING['host']
    >>> host
    'localhost'
    
    >>> port = layers.SELENIUM_PLONE_FUNCTIONAL_TESTING['port']
    >>> port
    55001
    
Let's now simulate a test. Test setup does nothing beyond what the base layers
do.

    >>> from plone.testing import z2, zca
    >>> zca.LAYER_CLEANUP.testSetUp()
    >>> z2.STARTUP.testSetUp()
    >>> layers.SELENIUM_FIXTURE.testSetUp()
    >>> layers.SELENIUM_PLONE_FUNCTIONAL_TESTING.testSetUp()
    
It is common in a test to use the Python API to change the state of
the server (e.g. create some content or change a setting) and then use
the Selenium browser to look at the results. Bear in mind that the
server is running in a separate thread, with a separate security
manager, so calls to ``helpers.login()`` and ``helpers.logout()``, for
instance, do not affect the server thread.
    
    >>> from plone.app.testing import helpers
    >>> from plone.app.testing.interfaces import TEST_USER_ID
    >>> portal = layers.SELENIUM_PLONE_FUNCTIONAL_TESTING['portal'] # would normally be self.layer['portal']
    >>> helpers.setRoles(portal, TEST_USER_ID, ['Manager'])
    >>> portal.invokeFactory('Folder', 'folder1')
    'folder1'

Note that we need to commit the transaction before it will show up in the
other thread.  This is important whenever your interactions with the
selenium browser are going to require retrieving content from the
server when that content needs to reflect changes you've made in your
test. For example, if some browser action invokes some AJAX code which
refreshes a part of the page from ZODB content, that refreshed content
will only reflect recent changes if you did transaction.commit()
before executing the browser action that triggered the AJAX.  The
plone.app.testing.selenium_layers.open() method does this for you when
opening a new URL, but there are many more ways to cause content
changes that pull from the ZODB when doing JavaScript testing so in
all other cases you are responsible to call transaction.commit()
yourself.

    >>> from plone.app.testing.selenium_layers import open
    >>> selenium = layers.SELENIUM_PLONE_FUNCTIONAL_TESTING['selenium']
    >>> open(selenium, portal.folder1.absolute_url())
    >>> selenium.get_title()
    u'folder1 \u2014 Plone site'

Now we also test logging-in to Plone. 

    >>> from plone.app.testing.selenium_layers import login
    >>> login(selenium, portal)
    >>> selenium.find_element_by_tag_name('h1').get_text()
    u'You are now logged in'

Test tear-down does nothing beyond what the base layers do.
    
    >>> layers.SELENIUM_PLONE_FUNCTIONAL_TESTING.testTearDown()
    >>> layers.SELENIUM_FIXTURE.testTearDown()
    >>> z2.STARTUP.testTearDown()
    >>> zca.LAYER_CLEANUP.testTearDown()

    >>> 'portal' in layers.SELENIUM_PLONE_FUNCTIONAL_TESTING
    False

    >>> 'app' in layers.SELENIUM_PLONE_FUNCTIONAL_TESTING
    False
    
    >>> 'request' in layers.SELENIUM_PLONE_FUNCTIONAL_TESTING
    False
    
    >>> with helpers.ploneSite() as portal:
    ...     print 'folder1' in portal.objectIds()
    False

When the layer is torn down, the Selenium browser is closed.

    >>> runner.tear_down_unneeded(options, [], setupLayers)
    Tear down plone.app.testing.selenium_layers.SeleniumTesting:Functional in ... seconds.
    Tear down plone.app.testing.layers.PloneFixture in ... seconds.
    Tear down plone.testing.z2.Startup in ... seconds.
    Tear down plone.testing.zca.LayerCleanup in ... seconds.

    >>> if getattr(selenium, '_server', None) is None:
    ...     import urllib2
    ...     urllib2.urlopen('http://XXX')
    ... else:
    ...     from selenium.remote.webdriver import WebDriver
    ...     WebDriver._execute(selenium, 'quit')
    Traceback (most recent call last):
    URLError: ...
