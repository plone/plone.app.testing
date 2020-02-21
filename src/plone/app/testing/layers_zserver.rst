Plone testing ZServer layers
----------------------------

There are some ZServer layers used to set up test fixtures containing a Plone
site running with ZServer. They are all importable from ``plone.app.testing``
directly, or from their canonical locations at ``plone.app.testing.layers``.

    >>> from plone.app.testing import layers

For testing, we need a testrunner

    >>> from zope.testrunner import runner

FTP server with Plone site
~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``PLONE_FTP_SERVER`` layer instantiates the ``FunctionalTesting`` class
with two bases: ``PLONE_FIXTURE``, as shown above, and ``FTP_SERVER_FIXTURE``
from ``plone.testing``, which starts up an FTP server thread.

    >>> "%s.%s" % (layers.PLONE_FTP_SERVER.__module__, layers.PLONE_FTP_SERVER.__name__,)
    'plone.app.testing.layers.Plone:FTPServer'

    >>> layers.PLONE_FTP_SERVER.__bases__
    (<Layer 'plone.app.testing.layers.PloneZServerFixture'>, <Layer 'plone.testing.zserver.FTPServer'>)

    >>> options = runner.get_options([], [])
    >>> setupLayers = {}
    >>> runner.setup_layer(options, layers.PLONE_FTP_SERVER, setupLayers)  # here!
    Set up plone.testing.zca.LayerCleanup in ... seconds.
    Set up plone.testing.zserver.Startup in ... seconds.
    Set up plone.app.testing.layers.PloneZServerFixture in ... seconds.
    Set up plone.testing.zserver.FTPServer in ... seconds.
    Set up plone.app.testing.layers.Plone:FTPServer in ... seconds.

After layer setup, the resources ``host`` and ``port`` are available, and
indicate where Zope is running.

    >>> host = layers.PLONE_FTP_SERVER['host']
    >>> host
    'localhost'

The port is auto-allocated

    >>> port = layers.PLONE_FTP_SERVER['port']
    >>> bool(port)
    True

Let's now simulate a test. Test setup does nothing beyond what the base layers
do.

    >>> from plone.testing import zca, zserver
    >>> zca.LAYER_CLEANUP.testSetUp()
    >>> zserver.STARTUP.testSetUp()
    >>> layers.PLONE_FIXTURE.testSetUp()
    >>> zserver.FTP_SERVER_FIXTURE.testSetUp()
    >>> layers.PLONE_FTP_SERVER.testSetUp()

It is common in a test to use the Python API to change the state of the server
(e.g. create some content or change a setting) and then use the FTP protocol
to look at the results. Bear in mind that the server is running in a separate
thread, with a separate security manager, so calls to ``helpers.login()`` and
``helpers.logout()``, for instance, do not affect the server thread.

    >>> from plone.app.testing import helpers
    >>> from plone.app.testing.interfaces import TEST_USER_ID
    >>> portal = layers.PLONE_FTP_SERVER['portal'] # would normally be self.layer['portal']
    >>> helpers.setRoles(portal, TEST_USER_ID, ['Manager'])
    >>> from OFS.Folder import Folder
    >>> portal._setObject('folder1', Folder('folder1'))
    'folder1'

Note that we need to commit the transaction before it will show up in the
other thread.

    >>> import transaction; transaction.commit()

    >>> folder_path = portal.absolute_url_path() + '/folder1'

    >>> import ftplib
    >>> ftpClient = ftplib.FTP()
    >>> ftpClient.connect(host, port, timeout=5)
    '220 ... FTP server (...) ready.'

    >>> from plone.app.testing.interfaces import SITE_OWNER_NAME
    >>> from plone.app.testing.interfaces import SITE_OWNER_PASSWORD

    >>> ftpClient.login(SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
    '230 Login successful.'

    >>> ftpClient.cwd(folder_path)
    '250 CWD command successful.'

    >>> ftpClient.retrlines('LIST')
    drwxrwx---   1 test_user_1_ Zope            0 ... .
    d---------   1 admin        Zope            0 ... ..
    '226 Transfer complete'

    >>> ftpClient.quit()
    '221 Goodbye.'

Test tear-down does nothing beyond what the base layers do.

    >>> layers.PLONE_FTP_SERVER.testTearDown()
    >>> zserver.FTP_SERVER_FIXTURE.testTearDown()
    >>> layers.PLONE_FIXTURE.testTearDown()
    >>> zserver.STARTUP.testTearDown()
    >>> zca.LAYER_CLEANUP.testTearDown()

    >>> 'portal' in layers.PLONE_FTP_SERVER
    False

    >>> 'app' in layers.PLONE_FTP_SERVER
    False

    >>> 'request' in layers.PLONE_FTP_SERVER
    False

    >>> import plone.testing.zserver
    >>> with helpers.ploneSite(flavour=plone.testing.zserver) as portal:
    ...     print('folder1' in portal.objectIds())
    False

When the server is torn down, the FTP server thread is stopped.

    >>> runner.tear_down_unneeded(options, [], setupLayers, [])
    Tear down plone.app.testing.layers.Plone:FTPServer in ... seconds.
    Tear down plone.testing.zserver.FTPServer in ... seconds.
    Tear down plone.app.testing.layers.PloneZServerFixture in ... seconds.
    Tear down plone.testing.zserver.Startup in ... seconds.
    Tear down plone.testing.zca.LayerCleanup in ... seconds.

    >>> ftpClient.connect(host, port, timeout=5) # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    error: [Errno 61] Connection refused
