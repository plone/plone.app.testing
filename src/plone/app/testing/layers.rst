Plone testing layers
--------------------

There are various layers used to set up test fixtures containing a Plone
site. They are all importable from ``plone.app.testing`` directly, or from
their canonical locations at ``plone.app.testing.layers``.

    >>> from plone.app.testing import layers

For testing, we need a testrunner

    >>> from zope.testrunner import runner


Plone site fixture
~~~~~~~~~~~~~~~~~~

The ``PLONE_FIXTURE`` layer extends ``STARTUP`` from ``plone.testing.zope`` to
set up a Plone site.

**Note:** This layer should only be used as a base layer, and not directly in
tests, since it does not manage the test lifecycle. To run a simple
integration test with this fixture, use the ``PLONE_INTEGRATION_TESTING``
layer described below. To run a simple functional test, use the
``PLONE_FUNCTIONAL_TESTING`` layer. Both of these have ``PLONE_FIXTURE`` as
a base. You can also extend ``PLONE_FIXTURE`` with your own fixture layer,
instantiating the ``IntegrationTesting`` or ``FunctionalTesting``classes
as appropriate. See this package's ``README`` file for details.

On layer setup, a new ``DemoStorage`` is stacked on top of the ``zodbDB``
resource (see ``plone.testing.zodb``). A fresh Plone with no default content
is created and added to the application root in this storage. The various
old-style products that Plone depends on are loaded, as is Plone's ZCML and
that of its direct dependencies. Before loading any ZCML, a new global
component registry is stacked on top of the default one (see
``plone.testing.zca``).

**Note**: A ZCML feature ``disable-autoinclude`` is set before Plone's ZCML is
loaded. This means that Plone will *not* automatically load the ZCML of
installed packages that use the ``z3c.autoinclude.plugin`` entry point. If you
want to use such packages, you should load their configuration explicitly.

Let's set up the fixture layer and inspect the state of the site.

    >>> options = runner.get_options([], [])
    >>> setupLayers = {}
    >>> runner.setup_layer(options, layers.PLONE_FIXTURE, setupLayers)  # doctest: +ELLIPSIS
      Set up plone.testing.zca.LayerCleanup in ... seconds.
      Set up plone.testing.zope.Startup in ... seconds.
      Set up plone.app.testing.layers.PloneFixture in ... seconds.


The application root's ``acl_users`` folder will have one user, whose name and
password are found in the constants ``SITE_OWNER_NAME`` and
``SITE_OWNER_PASSWORD``, in ``plone.app.testing.interfaces``. This user
has the ``Manager`` role, and is the owner of the site object. You should not
normally use this for testing, unless you need to manipulate the site itself.

    >>> from plone.testing import zope, zca
    >>> from plone.app.testing.interfaces import SITE_OWNER_NAME

    >>> with zope.zopeApp() as app:
    ...     print(app['acl_users'].getUser(SITE_OWNER_NAME))
    ...     print(sorted(app['acl_users'].getUser(SITE_OWNER_NAME).getRolesInContext(app)))
    admin
    ['Authenticated', 'Manager']

Inside the Plone site, the default theme is installed

    >>> from plone.app.testing import helpers
    >>> with helpers.ploneSite() as portal:
    ...     print(portal['portal_registry']['plone.app.theming.interfaces.IThemeSettings.rules'])
    /++theme++barceloneta/rules.xml

**Note:** Here, we have used the ``ploneSite`` context manager to get hold of
the Plone site root. Like ``zope.zopeApp()``, this is intended for use during
layer setup and tear-down, and will automatically commit any changes unless an
error is raised.

There is one user, whose user id, login name name and password are found in the
constants ``TEST_USER_ID``, ``TEST_USER_NAME`` and ``TEST_USER_PASSWORD`` in
the module ``plone.app.testing.interfaces``.

    >>> from plone.app.testing.interfaces import TEST_USER_NAME
    >>> with helpers.ploneSite() as portal:
    ...     print(portal['acl_users'].getUser(TEST_USER_NAME).getId())
    ...     print(portal['acl_users'].getUser(TEST_USER_NAME).getUserName())
    ...     print(sorted(portal['acl_users'].getUser(TEST_USER_NAME).getRolesInContext(portal)))
    test_user_1_
    test-user
    ['Authenticated', 'Member']

There is no default workflow or content:

    >>> with helpers.ploneSite() as portal:
    ...     print(portal['portal_workflow'].getDefaultChain())
    ()

Layer tear-down resets the environment.

    >>> runner.tear_down_unneeded(options, [], setupLayers, [])
    Tear down plone.app.testing.layers.PloneFixture in ... seconds.
    Tear down plone.testing.zope.Startup in ... seconds.
    Tear down plone.testing.zca.LayerCleanup in ... seconds.

Integration testing
~~~~~~~~~~~~~~~~~~~

``PLONE_INTEGRATION_TESTING`` can be used to run integration tests against the
fixture set up by the ``PLONE_FIXTURE`` layer.

    >>> "%s.%s" % (layers.PLONE_INTEGRATION_TESTING.__module__, layers.PLONE_INTEGRATION_TESTING.__name__,)
    'plone.app.testing.layers.Plone:Integration'

    >>> layers.PLONE_INTEGRATION_TESTING.__bases__
    (<Layer 'plone.app.testing.layers.PloneFixture'>,)

Let's set up the layers and attempt to run a test.

    >>> options = runner.get_options([], [])
    >>> setupLayers = {}
    >>> runner.setup_layer(options, layers.PLONE_INTEGRATION_TESTING, setupLayers)
    Set up plone.testing.zca.LayerCleanup in ... seconds.
    Set up plone.testing.zope.Startup in ... seconds.
    Set up plone.app.testing.layers.PloneFixture in ... seconds.
    Set up plone.app.testing.layers.Plone:Integration in ... seconds.

Let's now simulate a test

    >>> zca.LAYER_CLEANUP.testSetUp()
    >>> zope.STARTUP.testSetUp()
    >>> layers.PLONE_FIXTURE.testSetUp()
    >>> layers.PLONE_INTEGRATION_TESTING.testSetUp()

The portal is available as the resource ``portal``:

    >>> layers.PLONE_INTEGRATION_TESTING['portal'] # would normally be self.layer['portal']
    <PloneSite at /plone>

The local component site is set to the Plone site for the test:

    >>> from zope.component import getSiteManager
    >>> getSiteManager()
    <PersistentComponents /plone>

During the test, we are logged in as the test user:

    >>> from AccessControl import getSecurityManager
    >>> getSecurityManager().getUser()
    <PloneUser 'test-user'>

A new transaction is begun and aborted for each test, so we can create
content safely (so long as we don't commit):

    >>> from plone.app.testing.interfaces import TEST_USER_ID
    >>> portal = layers.PLONE_INTEGRATION_TESTING['portal'] # would normally be self.layer['portal']
    >>> helpers.setRoles(portal, TEST_USER_ID, ['Manager'])
    >>> from OFS.SimpleItem import SimpleItem
    >>> portal._setObject('d1', SimpleItem('d1'))
    'd1'
    >>> 'd1' in portal.objectIds()
    True

Let's now simulate test tear-down.

    >>> layers.PLONE_INTEGRATION_TESTING.testTearDown()
    >>> layers.PLONE_FIXTURE.testTearDown()
    >>> zope.STARTUP.testTearDown()
    >>> zca.LAYER_CLEANUP.testTearDown()

At this point, our transaction has been rolled back:

    >>> with helpers.ploneSite() as portal:
    ...     'd1' in portal.objectIds()
    False

We are also logged out again:

    >>> getSecurityManager().getUser()
    <SpecialUser 'Anonymous User'>

And the component site has been reset:

    >>> getSiteManager()
    <BaseGlobalComponents test-stack-2>

Layer tear-down resets the environment.

    >>> runner.tear_down_unneeded(options, [], setupLayers, [])
    Tear down plone.app.testing.layers.Plone:Integration in ... seconds.
    Tear down plone.app.testing.layers.PloneFixture in ... seconds.
    Tear down plone.testing.zope.Startup in ... seconds.
    Tear down plone.testing.zca.LayerCleanup in ... seconds.

Functional testing
~~~~~~~~~~~~~~~~~~

``PLONE_FUNCTIONAL_TESTING`` can be used to run functional tests against the
fixture set up by the ``PLONE_FIXTURE`` layer.

    >>> "%s.%s" % (layers.PLONE_FUNCTIONAL_TESTING.__module__, layers.PLONE_FUNCTIONAL_TESTING.__name__,)
    'plone.app.testing.layers.Plone:Functional'

    >>> layers.PLONE_FUNCTIONAL_TESTING.__bases__
    (<Layer 'plone.app.testing.layers.PloneFixture'>,)

Let's set up the layers and attempt to run a test.

    >>> options = runner.get_options([], [])
    >>> setupLayers = {}
    >>> runner.setup_layer(options, layers.PLONE_FUNCTIONAL_TESTING, setupLayers)
    Set up plone.testing.zca.LayerCleanup in ... seconds.
    Set up plone.testing.zope.Startup in ... seconds.
    Set up plone.app.testing.layers.PloneFixture in ... seconds.
    Set up plone.app.testing.layers.Plone:Functional in ... seconds.

Let's now simulate a test

    >>> zca.LAYER_CLEANUP.testSetUp()
    >>> zope.STARTUP.testSetUp()
    >>> layers.PLONE_FIXTURE.testSetUp()
    >>> layers.PLONE_FUNCTIONAL_TESTING.testSetUp()

    >>> layers.PLONE_FUNCTIONAL_TESTING['portal'] # would normally be self.layer['portal']
    <PloneSite at /plone>

    >>> from zope.component import getSiteManager
    >>> getSiteManager()
    <PersistentComponents /plone>

    >>> from AccessControl import getSecurityManager
    >>> getSecurityManager().getUser()
    <PloneUser 'test-user'>

A new ``DemoStorage`` is stacked for each test, so we can safely commit during
test execution.

    >>> portal = layers.PLONE_FUNCTIONAL_TESTING['portal'] # would normally be self.layer['portal']
    >>> helpers.setRoles(portal, TEST_USER_ID, ['Manager'])
    >>> portal._setObject('d1', SimpleItem('d1'))
    'd1'
    >>> import transaction; transaction.commit()
    >>> 'd1' in portal.objectIds()
    True

Let's now simulate test tear-down.

    >>> layers.PLONE_FUNCTIONAL_TESTING.testTearDown()
    >>> layers.PLONE_FIXTURE.testTearDown()
    >>> zope.STARTUP.testTearDown()
    >>> zca.LAYER_CLEANUP.testTearDown()

The previous database state should have been restored.

    >>> with helpers.ploneSite() as portal:
    ...     'd1' in portal.objectIds()
    False

Along with the rest of the state:

    >>> getSecurityManager().getUser()
    <SpecialUser 'Anonymous User'>

    >>> getSiteManager()
    <BaseGlobalComponents test-stack-2>

Layer tear-down resets the environment.

    >>> runner.tear_down_unneeded(options, [], setupLayers, [])
    Tear down plone.app.testing.layers.Plone:Functional in ... seconds.
    Tear down plone.app.testing.layers.PloneFixture in ... seconds.
    Tear down plone.testing.zope.Startup in ... seconds.
    Tear down plone.testing.zca.LayerCleanup in ... seconds.

HTTP server
~~~~~~~~~~~

The ``PLONE_WSGISERVER`` layer instantiates the ``FunctionalTesting`` class with
two bases: ``PLONE_FIXTURE``, as shown above, and ``WSGI_SERVER_FIXTURE`` from
``plone.testing``, which starts up a WSGI server. (There also the name
``PLONE_ZSERVER`` in place which is a BBB alias.)

    >>> "%s.%s" % (layers.PLONE_WSGISERVER.__module__, layers.PLONE_WSGISERVER.__name__,)
    'plone.app.testing.layers.Plone:WSGIServer'

    >>> layers.PLONE_WSGISERVER.__bases__
    (<Layer 'plone.app.testing.layers.PloneFixture'>, <Layer 'plone.testing.zope.WSGIServer'>)

    >>> options = runner.get_options([], [])
    >>> setupLayers = {}
    >>> runner.setup_layer(options, layers.PLONE_WSGISERVER, setupLayers)
    Set up plone.testing.zca.LayerCleanup in ... seconds.
    Set up plone.testing.zope.Startup in ... seconds.
    Set up plone.app.testing.layers.PloneFixture in ... seconds.
    Set up plone.testing.zope.WSGIServer in ... seconds.
    Set up plone.app.testing.layers.Plone:WSGIServer in ... seconds.

After layer setup, the resources ``host`` and ``port`` are available, and
indicate where Zope is running.

    >>> host = layers.PLONE_WSGISERVER['host']
    >>> host
    'localhost'

    >>> port = layers.PLONE_WSGISERVER['port']
    >>> import os
    >>> port > 0
    True

Let's now simulate a test. Test setup does nothing beyond what the base layers
do.

    >>> zca.LAYER_CLEANUP.testSetUp()
    >>> zope.STARTUP.testSetUp()
    >>> layers.PLONE_FIXTURE.testSetUp()
    >>> zope.WSGI_SERVER_FIXTURE.testSetUp()
    >>> layers.PLONE_ZSERVER.testSetUp()

It is common in a test to use the Python API to change the state of the server
(e.g. create some content or change a setting) and then use the HTTP protocol
to look at the results. Bear in mind that the server is running in a separate
thread, with a separate security manager, so calls to ``helpers.login()`` and
``helpers.logout()``, for instance, do not affect the server thread.

    >>> portal = layers.PLONE_ZSERVER['portal'] # would normally be self.layer['portal']
    >>> helpers.setRoles(portal, TEST_USER_ID, ['Manager'])
    >>> portal.title = 'Fancy Portal'

Note that we need to commit the transaction before it will show up in the
other thread.

    >>> import transaction; transaction.commit()

We can now look for this new object through the server.

    >>> portal_url = portal.absolute_url()
    >>> portal_url.split(':')[:-1]
    ['http', '//localhost']

    >>> from six.moves.urllib.request import urlopen
    >>> conn = urlopen(portal_url, timeout=10)
    >>> responseBody = conn.read()
    >>> b"Fancy Portal" in responseBody
    True
    >>> conn.close()

Test tear-down does nothing beyond what the base layers do.

    >>> layers.PLONE_ZSERVER.testTearDown()
    >>> zope.WSGI_SERVER_FIXTURE.testTearDown()
    >>> layers.PLONE_FIXTURE.testTearDown()
    >>> zope.STARTUP.testTearDown()
    >>> zca.LAYER_CLEANUP.testTearDown()

    >>> 'portal' in layers.PLONE_ZSERVER
    False

    >>> 'app' in layers.PLONE_ZSERVER
    False

    >>> 'request' in layers.PLONE_ZSERVER
    False

    >>> with helpers.ploneSite() as portal:
    ...     print('folder1' in portal.objectIds())
    False

When the server is torn down, the ZServer thread is stopped.

    >>> runner.tear_down_unneeded(options, [], setupLayers, [])
    Tear down plone.app.testing.layers.Plone:WSGIServer in ... seconds.
    Tear down plone.testing.zope.WSGIServer in ... seconds.
    Tear down plone.app.testing.layers.PloneFixture in ... seconds.
    Tear down plone.testing.zope.Startup in ... seconds.
    Tear down plone.testing.zca.LayerCleanup in ... seconds.

    >>> import requests
    >>> requests.get(portal_url + '/folder1') # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    requests.exceptions.ConnectionError: ...


Mock MailHost
~~~~~~~~~~~~~

The fixture ``MOCK_MAILHOST_FIXTURE`` layer
allows to replace the Zope MailHost with a dummy one.

**Note:** This layer builds on top of ``PLONE_FIXTURE``.
Like ``PLONE_FIXTURE``, it should only be used as a base layer,
and not directly in tests.
See this package's ``README`` file for details.

    >>> layers.MOCK_MAILHOST_FIXTURE.__bases__
    (<Layer 'plone.app.testing.layers.PloneFixture'>,)
    >>> options = runner.get_options([], [])
    >>> setupLayers = {}
    >>> runner.setup_layer(options, layers.MOCK_MAILHOST_FIXTURE, setupLayers)
    Set up plone.testing.zca.LayerCleanup in ... seconds.
    Set up plone.testing.zope.Startup in ... seconds.
    Set up plone.app.testing.layers.PloneFixture in ... seconds.
    Set up plone.app.testing.layers.MockMailHostLayer in ... seconds.

Let's now simulate a test.
Test setup sets a couple of registry records and
replaces the mail host with a dummy one:

    >>> from zope.component import getUtility
    >>> from plone.registry.interfaces import IRegistry

    >>> zca.LAYER_CLEANUP.testSetUp()
    >>> zope.STARTUP.testSetUp()
    >>> layers.MOCK_MAILHOST_FIXTURE.testSetUp()

    >>> with helpers.ploneSite() as portal:
    ...     registry = getUtility(IRegistry, context=portal)

    >>> registry["plone.email_from_address"]
    'noreply@example.com'
    >>> registry["plone.email_from_name"]
    'Plone site'

The dummy MailHost, instead of sending the emails,
stores them in a list of messages:

    >>> with helpers.ploneSite() as portal:
    ...     portal.MailHost.messages
    []

If we send a message, we can check it in the list:

    >>> with helpers.ploneSite() as portal:
    ...     portal.MailHost.send(
    ...         "Hello world!",
    ...         mto="foo@example.com",
    ...         mfrom="bar@example.com",
    ...         subject="Test",
    ...         msg_type="text/plain",
    ...     )
    >>> with helpers.ploneSite() as portal:
    ...     for message in portal.MailHost.messages:
    ...         print(message.decode("utf-8"))
    MIME-Version: 1.0
    Content-Type: text/plain
    Subject: Test
    To: foo@example.com
    From: bar@example.com
    Date: ...
    <BLANKLINE>
    Hello world!

The list can be reset:

    >>> with helpers.ploneSite() as portal:
    ...     portal.MailHost.reset()
    ...     portal.MailHost.messages
    []

When the test is torn down the original MaiHost is restored
and the registry is cleaned up:

    >>> layers.MOCK_MAILHOST_FIXTURE.testTearDown()
    >>> zope.STARTUP.testTearDown()
    >>> zca.LAYER_CLEANUP.testTearDown()

    >>> with helpers.ploneSite() as portal:
    ...     portal.MailHost.messages
    Traceback (most recent call last):
    ...
    AttributeError: 'RequestContainer' object has no attribute 'messages'

    >>> registry["plone.email_from_address"]
    >>> registry["plone.email_from_name"]
    >>> runner.tear_down_unneeded(options, [], setupLayers, [])
    Tear down plone.app.testing.layers.MockMailHostLayer in ... seconds.
    Tear down plone.app.testing.layers.PloneFixture in ... seconds.
    Tear down plone.testing.zope.Startup in ... seconds.
    Tear down plone.testing.zca.LayerCleanup in ... seconds.
