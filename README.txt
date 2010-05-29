Introduction
============

.. contents:: Table of contents

``plone.app.testing`` provides tools for writing integration and functional
tests for code that runs on top of Plone. It is based on `plone.testing`_.
If you are unfamiliar with ``plone.testing``, the concept of layers, or the
`zope.testing`_ testrunner, please take a look at the the ``plone.testing``
documentation. In fact, even if you are working exclusively with Plone, you
are likely to want to use some of its features for unit testing.

In short, ``plone.app.testing`` includes:

* A set of layers that set up fixtures containing a Plone site, intended for
  writing integration and functional tests.
* A collection of helper functions, some useful for writing your own layers
  and some applicable to tests themselves.
* A convenient layer base class, extending ``plone.testing.Layer``, which
  makes it easier to write custom layers extending the Plone site fixture,
  with proper isolation and tear-down.
* Cleanup hooks for ``zope.testing.cleanup`` to clean up global state found
  in a Plone installation. This is useful for unit testing.

Compatibility
-------------

``plone.app.testing`` works with Plone 4 and Zope 2.12. It may work with
newer versions. It will not work with earlier versions.

Installation and usage
======================

To use ``plone.app.testing`` in your own package, you need to add it as a
dependency. Most people prefer to keep test-only dependencies separate, so
that they do not need to be installed in scenarios (such as on a production
server) where the tests will not be run. This can be achieved using a
``test`` extra.

In ``setup.py``, add or modify the ``extras_require`` option, like so::

    extras_require = {
        'test': [
                'plone.app.testing',
            ]
    },

This will also include ``plone.testing``, with the ``[z2]]``, ``[zca]`` and
``[zodb]`` extras (which ``plone.app.testing`` itself relies on).

Please see the `plone.testing`_ documentation for more details about how to
add a test runner to your buildout, and how to write and run tests.

Layer reference
===============

This package contains a layer class, ``plone.app.testing.layers.PloneSite``,
which sets up a Plone site fixture. It is combined with other layers from
`plone.testing`_ to provide a number of layer instances. It is important to
realise that these layers all have the same fundamental fixture: they just
manage test setup and tear-down differently.

When set up, the fixture will:

* Create a ZODB sandbox, via a stacked ``DemoStorage``. This ensures
  persistent changes made during layer setup can be cleanly torn down.
* Configure a global component registry sandbox. This ensures that global
  component registrations (e.g. as a result of loading ZCML configuration)
  can be cleanly torn down.
* Create a configuration context with the ``disable-autoinclude`` feature
  set. This has the effect of stopping Plone from automatically loading the
  configuration of any installed package that uses the
  ``z3c.autoinclude.plugin:plone`` entry point via `z3c.autoinclude`_. (This
  is to avoid accidentally polluting the test fixture - custom layers should
  load packages' ZCML configuration explicitly if required).
* Install a number of Zope 2-style products on which Plone depends.
* Load the ZCML for these products, and for ``Products.CMFPlone``, which in
  turn pulls in the configuration for the core of Plone.
* Create a default Plone site, with the default theme enabled, but with no
  default content.
* Add a user to the root user folder with the ``Manager`` role.
* Add a test user to this instance with the ``Member`` role.

For each test:

* The test user is logged in
* The local component site is set
* Various global caches are cleaned up

Various constants in the module ``plone.app.testing.interfaces`` are defined
to describe this environment:

+----------------------+--------------------------------------------------+
| **Constant**         | **Purpose**                                      |
+----------------------+--------------------------------------------------+
| PLONE_SITE_ID        | The id of the Plone site object inside the Zope  |
|                      | application root.                                |
+----------------------+--------------------------------------------------+
| PLONE_SITE_TITLE     | The title of the Plone site                      |
+----------------------+--------------------------------------------------+
| DEFAULT_LANGUAGE     | The default language of the Plone site ('en')    |
+----------------------+--------------------------------------------------+
| TEST_USER_NAME       | The username of the test user                    |
+----------------------+--------------------------------------------------+
| TEST_USER_PASSWORD   | The password of the test user                    |
+----------------------+--------------------------------------------------+
| TEST_USER_ROLES      | The default global roles of the test user -      |
|                      | ('Member',)                                      |
+----------------------+--------------------------------------------------+
| SITE_OWNER_NAME      | The username of the user owning the Plone site.  |
+----------------------+--------------------------------------------------+
| SITE_OWNER_PASSWORD  | The password of the user owning the Plone site.  |
+----------------------+--------------------------------------------------+

All the layers also expose a resource in addition to those from their
base layers, made available during tests:

``portal``
   The Plone site root.

Plone site - integration testing
--------------------------------

+------------+--------------------------------------------------+
| Layer:     | ``plone.app.testing.PLONE_INTEGRATION_TESTING``  |
+------------+--------------------------------------------------+
| Class:     | ``plone.app.testing.layers.PloneSite``           |
+------------+--------------------------------------------------+
| Bases:     | ``plone.testing.z2.INTEGRATION_TESTING``         |
+------------+--------------------------------------------------+
| Resources: | ``portal`` (test setup only)                     |
+------------+--------------------------------------------------+

This is the layer you are likely to use most often. It sets up a transaction
for each test, which is rolled back after each test.

See the description of the ``z2.INTEGRATION_TESTING`` layer in
`plone.testing`_ for details.

Plone site - functional testing
-------------------------------

+------------+--------------------------------------------------+
| Layer:     | ``plone.app.testing.PLONE_FUNCTIONAL_TESTING``   |
+------------+--------------------------------------------------+
| Class:     | ``plone.app.testing.layers.PloneSite``           |
+------------+--------------------------------------------------+
| Bases:     | ``plone.testing.z2.FUNCTIONAL_TESTING``          |
+------------+--------------------------------------------------+
| Resources: | ``portal`` (test setup only)                     |
+------------+--------------------------------------------------+

This is layer is intended for functional testing, e.g. using
`zope.testbrowser`.

See the description of the ``z2.FUNCTIONAL_TESTING`` layer in `plone.testing`_
for details.

Plone site - ZServer
--------------------

+------------+--------------------------------------------------+
| Layer:     | ``plone.app.testing.PLONE_ZSERVER``              |
+------------+--------------------------------------------------+
| Class:     | ``plone.testing.z2.ZServer``                     |
+------------+--------------------------------------------------+
| Bases:     | ``plone.app.testing.PLONE_FUNCTIONAL_TESTING``   |
+------------+--------------------------------------------------+
| Resources: | ``portal`` (test setup only)                     |
+------------+--------------------------------------------------+

This is layer is intended for functional testing using a live, running HTTP
server, e.g. using Selenium or Windmill.

See the description of the ``z2.ZSERVER`` layer in `plone.testing`_
for details.

Plone site - FTP server
-----------------------

+------------+--------------------------------------------------+
| Layer:     | ``plone.app.testing.PLONE_FTP_SERVER``           |
+------------+--------------------------------------------------+
| Class:     | ``plone.testing.z2.ZServer``                     |
+------------+--------------------------------------------------+
| Bases:     | ``plone.app.testing.PLONE_FUNCTIONAL_TESTING``   |
+------------+--------------------------------------------------+
| Resources: | ``portal`` (test setup only)                     |
+------------+--------------------------------------------------+

This is layer is intended for functional testing using a live, running HTTP
server, e.g. using Selenium or Windmill.

See the description of the ``z2.FTP_SERVER`` layer in `plone.testing`_
for details.

Helper functions
================

A number of helper functions are provided for use in tests and custom layers.

Plone site context manager
--------------------------

``ploneSite(db=None, connection=None, environ=None)``
    Use this context manager to access and make changes to the Plone site
    during layer setup. In most cases, you will use it without arguments,
    but if you have special needs, you can tie it to a particular database
    instance. See the description of the ``zopeApp()`` context manager in
    `plone.testing`_ (which this context manager uses internally) for details.
    
    The usual pattern is to call it during ``setUp()`` or ``tearDown()`` in
    your own layers::
        
        from plone.testing import Layer
        from plone.app.testing import ploneSite
        
        class MyLayer(Layer):
        
            def setUp(self):
            
                ...
            
                with ploneSite() as portal:
                
                    # perform operations on the portal, e.g.
                    portal.title = u"New title"
    
    Here, ``portal`` is the Plone site root. A transaction is begun before
    entering the ``with`` block, and will be committed upon exiting the block,
    unless an exception is raised, in which case it will be rolled back.
    
    Inside the block, the local component site is set to the Plone site root,
    so that local component lookups should work.
    
    **Note:** You should not use this in a test, or in a ``testSetUp()`` or
    ``testTearDown()`` method of a layer based on one of the layer in this
    package. Use the ``portal`` resource instead.
    
    **Also note:** If you are writing a layer setting up a Plone site fixture,
    you may want to use the ``PloneSandboxLayer`` layer base class, and
    implement the ``setUpPloneSite()`` and/or ``tearDownPloneSite()`` methods
    instead, both of which are passed the portal as an argument. See below.

User management
---------------

``login(portal, userName)``
    Simulate login as the given user. This is based on the ``z2.login()``
    helper in `plone.testing`_, but instead of passing a specific user folder,
    you pass the portal (e.g. as obtained via the ``portal`` layer resource).
    
    For example::
        
        import unittest2 as unittest
        
        from plone.app.testing import PLONE_INTEGRATION_TESTING
        from plone.app.testing import TEST_USER_NAME
        from plone.app.testing import login
        
        ...
        
        class MyTest(unittest.TestCase):
        
            layer = PLONE_INTEGRATION_TESTING
        
            def test_something(self):
                portal = self.layer['portal']
                login(portal, TEST_USER_NAME)
                
                ...

``logout()``
    Simulate logging out, i.e. becoming the anonymous user. This is equivalent
    to the ``z2.logout()`` helper in `plone.testing`_.
    
    For example::
    
        import unittest2 as unittest
        
        from plone.app.testing import PLONE_INTEGRATION_TESTING
        from plone.app.testing import logout
        
        ...
        
        class MyTest(unittest.TestCase):
        
            layer = PLONE_INTEGRATION_TESTING
        
            def test_something(self):
                portal = self.layer['portal']
                logout()
                
                ...

``setRoles(portal, userName, roles)``
    Set the roles for the given user. ``roles`` is a list of roles.
    
    For example:
    
        import unittest2 as unittest
        
        from plone.app.testing import PLONE_INTEGRATION_TESTING
        from plone.app.testing import TEST_USER_NAME
        from plone.app.testing import setRoles
        
        ...
        
        class MyTest(unittest.TestCase):
        
            layer = PLONE_INTEGRATION_TESTING
        
            def test_something(self):
                portal = self.layer['portal']
                setRoles(portal, TEST_USER_NAME, ['Manager'])

Product and profile installation
--------------------------------

``quickInstallProduct(portal, productName, reinstall=False)``
    Use this function to install a particular product into the given Plone
    site, using the ``portal_quickinstaller`` tool. If ``reinstall`` is
    ``False`` and the product is already installed, nothing will happen; if
    ``reinstall`` is ``True``, the product will be reinstalled. The
    ``productName`` should be a full dotted name, e.g. ``Products.MyProduct``,
    or ``my.product``.
    
    For example::
        
        from plone.testing import Layer
        
        from plone.app.testing import ploneSite
        from plone.app.testing import quickInstallProduct
        
        ...
        
        class MyLayer(Layer):
        
            ...
            
            def setUp(self):
                
                ...
                
                with ploneSite() as portal:
                    quickInstallProduct(portal, 'my.product')
                    
                    ...

``applyProfile(portal, profileName)``
    Install a GenericSetup profile (usually an extension profile) by name,
    using the ``portal_setup`` tool. The name is normally made up of a package
    name and a profile name. Do not use the ``profile-`` prefix.
    
    For example::
    
        from plone.testing import Layer
        
        from plone.app.testing import ploneSite
        from plone.app.testing import applyProfile
        
        ...
        
        class MyLayer(Layer):
        
            ...
            
            def setUp(self):
                
                ...
                
                with ploneSite() as portal:
                    applyProfile(portal, 'my.product:default')
                    
                    ...

Component architecture sandboxing
---------------------------------

``pushGlobalRegistry(portal, new=None, name=None)``
    Create or obtain a stack of global component registries, and push a new
    registry to the top of the stack. This allows Zope Component Architecture
    registrations (e.g. loaded via ZCML) to be effectively torn down.
    
    If you are going to use this function, please read the corresponding
    documentation for ``zca.pushGlobalRegistry()`` in `plone.testing`_. In
    particular, note that you *must* reciprocally call ``popGlobalRegistry()``
    (see below).
    
    This helper is based on ``zca.pushGlobalRegistry()``, but will also fix
    up the local component registry in the Plone site ``portal`` so that it
    has the correct bases.
    
    For example::
    
        from plone.testing import Layer
        
        from plone.app.testing import ploneSite
        from plone.app.testing import pushGlobalRegistry
        from plone.app.testing import popGlobalRegistry
        
        ...
        
        class MyLayer(Layer):
        
            ...
            
            def setUp(self):
                
                ...
                
                with ploneSite() as portal:
                    pushGlobalRegistry(portal)
                    
                    ...

``popGlobalRegistry(portal)``
    Tear down the top of the component architecture stack, as created with
    ``pushGlobalRegistry()``
    
    For example::
        
        ...
        
            def tearDown(self):
                
                with ploneSite() as portal:
                    popGlobalRegistry(portal)

Global state cleanup
--------------------

``tearDownProfileRegistation(productName)``
    GenericSetup profile registrations, e.g. as registered with the
    ``<genericsetup:registerProfile />`` ZCML directive, are made into a
    global registry. If you load the configuration for a package that
    registers such a profile, you should ensure that registration is torn
    down in your layer's ``tearDown()`` method. Pass a package/product name,
    and all profiles associated with that package will be cleared from the
    registry.
    
    For example::
    
        from plone.testing import Layer
        
        from plone.app.testing import ploneSite
        from plone.app.testing import tearDownProfileRegistration
        
        ...
        
        class MyLayer(Layer):
        
            ...
            
            def tearDown(self):
                
                tearDownProfileRegistration('my.product')
                
                ...
    
    **Note:** If your product also registered custom import or export steps,
    you should tear those down as well. There is no need for a helper here,
    just use the API::
    
        from Products.GenericSetup import _import_step_registry
        from Products.GenericSetup import _export_step_registry
        
        _import_step_registry.unregisterStep('import-step-id')
        _export_step_registry.unregisterStep('export-step-id')
    
    **Also note:** If you use the ``PloneSandboxLayer`` layer base class,
    this will snapshot the registries and tear them down for you.
    
``tearDownMultiPluginRegistration(pluginName)``
    PluggableAuthService "MultiPlugins" are kept in a global registry. If
    you have registered a plugin, e.g. using the ``registerMultiPlugin()``
    API, you should tear that registration down in your layer's ``tearDown()``
    method. You can use this helper, passing a plugin name.
    
    For example::
    
        from plone.testing import Layer
        
        from plone.app.testing import ploneSite
        from plone.app.testing import tearDownMultiPluginRegistration
        
        ...
        
        class MyLayer(Layer):
        
            ...
            
            def tearDown(self):
                
                tearDownMultiPluginRegistration('MyPlugin')
                
                ...

Layer base class
================

If you are writing a custom layer to test your own Plone add-on product, you
will often want to do the following on setup:

1. Stack a new ``DemoStorage`` on top of the one from the base layer. This
   ensures that any persistent changes performed during layer setup can be
   torn down completely, simply by popping the demo storage.

2. Push a new global component registry. This allows you to register
   components (e.g. by loading ZCML or using the test API from
   ``zope.component``) and tear down those registration easily by popping the
   component registry.

3. Load your product's ZCML configuration

4. Install the product into the test fixture Plone site

Of course, you may wish to make other changes to, such as creating some base
content or changing some settings.

On tear-down, you will then want to:

1. Remove any GenericSetup profiles and import/export steps that were loaded
   into the global registries during setup.

2. Pop the global component registry to unregister components loaded via ZCML.

3. Pop the ``DemoStorage`` to undo any persistent changes.

If you have made other changes on setup that are not covered by this broad
tear-down, you'll also want to tear those down explicitly here.

Stacking a demo storage and component registry and snapshotting the
GenericSetup profile registry is the safest way to avoid fixtures bleeding
between tests. However, it can be tricky to ensure that everything happens in
the right order.

To make things easier, you can use the ``PloneSandboxLayer`` layer base class.
This extends ``plone.testing.Layer`` and implements ``setUp()`` and
``tearDown()`` for you. You simply have to override one or both of the
following methods:

``setUpPloneSite(self, portal)``
    This is called during setup. ``portal`` is the Plone site root as
    configured by the ``ploneSite()`` context manager. This is the place to
    perform any custom setup.
    
    Implementing this method is mandatory.

``tearDownPloneSite(self, portal)``
    This is called during tear-down, before the global component registry and
    stacked ``DemoStorage`` are popped. Use this to tear down any additional
    global state.
    
    Implementing this method is optional. It may be useful e.g. if you want to
    use ``tearDownMultiPluginRegistration()`` to tear down a custom PAS plugin
    registration.
    
    **Note:** Because the layer snapshots the ``GenericSetup`` profile
    registry, it is not necessary to use ``tearDownProfileRegistation()`` to
    tear down GenericSetup profile registrations

Let's show a more comprehensive example of what such a layer may look like.
Imagine we have a product ``my.product``. It has a ``configure.zcml`` file
that loads some components and registers a ``GenericSetup`` profile, making it
installable in the Plone site. On layer setup, we want to load the product's
configuration and install it into the Plone site.

The layer would conventionally live in a module ``testing.py`` at the root of
the package, i.e. ``my.product.testing``::

    from plone.app.testing import PloneSandboxLayer
    from plone.app.testing import quickInstallProduct
    from plone.app.testing import PLONE_INTEGRATION_TESTING
    
    from zope.configuration import xmlconfig
    
    class MyProduct(PloneSandboxLayer):
    
        defaultBases = (PLONE_INTEGRATION_TESTING,)
        
        def setUpPloneSite(self, portal):
            
            # Load ZCML
            import my.product
            xmlconfig.file('configure.zcml', my.product, context=self['configurationContext'])
            
            # Install into Plone site using quickinstaller tool
            quickInstallProduct('my.product')
            
    MY_PRODUCT_INTEGRATION_TESTING = MyProduct()

Of course, we could do a lot more here. For example, let's say the product
had a content type 'my.product.page' and we wanted to create some test
content. We could do that with::

    from plone.app.testing import TEST_USER_NAME
    from plone.app.testing import setRoles
    
    ...
    
        def setUpPloneSite(self, portal):
            
            ...
            
            z2.setRoles(portal, TEST_USER_NAME, ['Manager'])
            z2.login(portal, TEST_USER_NAME)
            portal.invokeFactory('my.product.page', 'page-1', title=u"Page 1")
            z2.setRoles(portal, TEST_USER_NAME, ['Member'])
    
    ...
    
Note that unlike in a test, there is no user logged in at layer setup time,
so we have to explicitly log in as the test user. Here, we also grant the test
user the ``Manager`` role temporarily, to allow object construction (which
performs an explicit permission check).

    **Note:** Automatic tear down suffices for all the test setup above. If
    the only changes made during layer setup are to persistent, in-ZODB data,
    the global component registry, or the GenericSetup profiles registry, then
    no additional tear-down is required. For any other global state being
    managed, you should write a ``tearDownPloneSite()`` method to perform the
    necessary cleanup.

Given this layer, we could write a test (e.g. in ``tests.py``) like::
    
    import unittest2 as unittest
    from my.product.testing import MY_PRODUCT_INTEGRATION_TESTING
    
    class IntegrationTest(unittest.TestCase):
        
        layer = MY_PRODUCT_INTEGRATION_TESTING
        
        def test_page_dublin_core_title(self):
            portal = self.layer['portal']
            
            page1 = portal['page-1]
            page1.title = u"Some title"
            
            self.assertEqual(page1.Title(), u"Some title")
    
Please see `plone.testing`_ for more information about how to write and run
tests and assertions.

Common test patterns
====================

`plone.testing`_'s documentation contains details about the fundamental
techniques for writing tests of various kinds. In a Plone context, however,
some patterns tend to crop up time and again. Below, we will attempt to
catalog some of the more commonly used patterns via short code samples.

The examples in this section are all intended to be part of a test method.
Some may also be useful in layer set-up/tear-down. We have used ``unittest``
syntax here, although most of these examples could equally be adopted to
doctests.

We will assume that you are using the ``PLONE_INTEGRATION_TESTING`` or
``PLONE_FUNCTIONAL_TESTING`` layer, or a derivative. We will also assume
that the variables ``app``, ``portal`` and ``request`` are defined from the
relative layer resources, e.g. with::

    app = self.layer['app']
    portal = self.layer['portal']
    request = self.layer['request']

Note that in a doctest set up using the ``layered()`` function from
``plone.testing``, ``layer`` is in the global namespace, so you would do e.g.
``portal = layer['portal']``.

We will also assume the following imports have been made::

    import unittest2 as unittest
    
    from plone.app.testing import helpers
    from plone.app.testing import TEST_USER_NAME

Note that the helper functions can also be imported directly from
``plone.app.testing``, but it is easier to illustrate which methods are being
used by being explicit, e.g. ``helpers.login()`` is the function
``plone.app.testing.helpers.login()``.

Where other imports are required, they are shown alongside the code example.

Basic content management
------------------------

To create a content item of type 'Folder' with the id 'f1' in the root of
the portal::

    portal.invokeFactory('Folder', 'f1', title=u"Folder 1")

The ``title`` argument is optional. Other basic properties, like
``description``, can be set as well.

Note that this may fail with an ``Unauthorized`` exception, since the test
user won't normally have permissions to add content in the portal root.
You can set the roles of the test user to ensure that he has the necessary
permissions::
    
    helpers.setRoles(portal, TEST_USER_NAME, ['Manager'])
    portal.invokeFactory('Folder', 'f1', title=u"Folder 1")

To obtain an instance of this object::

    f1 = portal['f1']

To check an attribute of this object::

    self.assertEqual(f1.Title(), u"Folder 1")

The object can also be modified::

    f1.setTitle(u"Some title")

If you need those changes to show up in the ``portal_catalog``::

    f1.reindexObject()

To add another item inside the folder::

    f1.invokeFactory('Document', 'd1', title=u"Document 1")
    d1 = f1['d1']

To check if an object is in a container::

    self.assertTrue('f1' in portal)

To delete an object from a container:

    del portal['f1']

Searching
---------

To obtain the ``portal_catalog`` tool::

    from Products.CMFCore.utils import getToolByName
    
    catalog = getToolByName(portal, 'portal_catalog')

To search the catalog::

    results = catalog(portal_type="Document")

Keyword arguments are search parameters. The result is a lazy list. You can
call ``len()`` on it to get the number of search results, or iterate through
it. The items in the list are catalog brains. They have attributes that
correspond to the "metadata" columns configured for the catalog, e.g.
``Title``, ``Description``, etc. Note that these are simple attributes (not
methods), and contain the value of the corresponding attribute or method from
the source object at the time the object was cataloged (i.e. they are not
necessarily up to date).

To get the path of a given item in the search results::

    for brain in results:
        path = brain.getPath()

To get an absolute URL::

    for brain in results:
        url = brain.getURL()

To get the original object::

    for brain in results:
        obj = brain.getObject()

To re-index an object so that its catalog information is up to date::

    item.reindexObject()

User management
---------------

To create a new user::

    portal['acl_users'].userFolderAddUser('user1', 'secret', ['Member'], [])

The arguments are the username (which will also be the user id), the password,
a list of roles, and a list of domains (rarely used).

To make a particular user active in the integration testing environment::

    helpers.login(portal, 'user1')

To log out (become anonymous)::

    helpers.logout()

To obtain the current user::

    from AccessControl import getSecurityManager
    
    user = getSecurityManager().getUser()

To obtain a user by name::
    
    user = portal['acl_user'].getUser('user1')

Or by user id (id and username are often the same in tests, but are often
different in real-world scenarios)::

    user = portal['acl_user'].getUserById('user1')

To get the user's user name::

    userName = user.getUserName()

To get the user's id::

    userId = user.getId()

Permissions and roles
---------------------

To get a user's roles in a particular context (taking local roles into
account)::
    
    from AccessControl import getSecurityManager
    
    user = getSecurityManager().getUser()
    roles = user.getRolesInContext(portal)
    
    self.assertEquals(roles, ['Member'])

To change a user's roles::

    helpers.setRoles(portal, TEST_USER_NAME, ['Member', 'Manager'])

To grant local roles to a user in the folder f1::

    f1.manage_setLocalRoles(TEST_USER_NAME, ['Reviewer'])

To check the local roles of a given user in the folder 'f1'::

    localRoles = f1.get_local_roles_for_userid(TEST_USER_NAME)
    self.assertEqual(localRoles, ['Reviewer'])

To grant the 'View' permission to the roles 'Member' and 'Manager' in the
portal root without acquiring additional roles from its parents::

    portal.manage_permission('View', ['Member', 'Manager'], acquire=False)

This can also be invoked on a folder or individual content item.

To assert which roles have a given the permission 'View' in the context of the
portal::

    roles = [r['name'] for r in portal.rolesOfPermission('View') if r['selected']]
    self.assertEqual(roles, ['Member', 'Manager'])

To assert which permissions have been granted to the 'Reviewer' role in the
context of the folder f1::

    permissions = [p['name'] for p in f1.permissionsOfRole('Reviewer') if p['selected']]
    self.assertEqual(permissions, ['Review portal content'])

To add a new role::

    portal._addRole('Tester')

To assert the roles available in a given context::
    
    roles = portal.valid_roles()
    self.assertTrue('Tester' in roles)

Workflow
--------

To get the default workflow chain::
    
    from Products.CMFCore.utils import getToolByName
    
    workflowTool = getToolByName(portal, 'portal_workflow)
    
    defaultChain = workflowTool.getDefaultChain()
    self.assertEqual(defaultChain, ('my_workflow',))

To set the default workflow chain::
    
    workflowTool.setDefaultChain('my_workflow')

To set a multi-workflow chain, separate workflows by spaces or commas.

To get the workflow chain for the portal type 'Document':

    chains = dict(workflowTool.listChainOverrides())
    defaultChain = workflowTool.getDefaultChain()
    documentChain = chains.get('Document', defaultChain)
    
    self.assertEqual(documentChain, ('my_other_workflow',))

To get the current workflow chain for the content object f1::
    
    chain = workflowTool.getChainFor(f1)

To set the workflow chain for the 'Document' type::
    
    workflowTool.setChainForPortalTypes(('Document',), 'my_workflow')

You can pass multiple type names to set multiple chains at once. To set a
multi-workflow chain, separate workflow names by commas. To indicate that a
type should use the default workflow, use the special chain name '(Default)'.

To update all permissions after changing the workflow::
    
    workflowTool.updateRoleMappings()

To check the current workflow state of the content object f1::
    
    state = workflowTool.getInfoFor(f1, 'review_state')
    self.assertEqual(state, 'published')

To change the workflow state of the content object f1 by invoking the
transaction 'publish'::
    
    workflowTool.doActionFor(f1, 'publish')

Note that this performs an explicit permission check, so if the current user
doesn't have permission to perform this workflow action, you may get an error
indicating the action is not available. If so, use ``login()`` or
``setRoles()`` to ensure the current user is able to change the workflow
state.

Installing products and extension profiles
------------------------------------------

To install an add-on product into the Plone site::
    
    TODO

To apply a particular extension profile::
    
    TODO

Note that both of these assume the product's ZCML has been loaded. See the
layer examples above for more details on how to do that.

When writing a product that has an installation extension profile, it is often
desirable to write tests that inspect the state of the site after the profile
has been applied. Some of the more common such tests are shown below.

To verify that a product has been installed (e.g. via ``metadata.xml``)::
    
    TODO

To verify that a particular content type has been installed (e.g. via
``types.xml``)::

    TODO

To verify that a new catalog index has been installed (e.g. via
``catalog.xml``)::

    TODO

To verify that a new catalog metadata column has been added (e.g. via
``catalog.xml``)::

    TODO

To verify that a new workflow has been installed (e.g. via
``workflows.xml``)::

    TODO
    
To verify that a new workflow has been assigned to a type (e.g. via
``workflows.xml``)::
    
    TODO
    
To verify that a new workflow has been set as the default (e.g. via
``workflows.xml``)::

    TODO

To test the value of a property in the ``portal_properties`` tool (e.g. set
via ``propertiestool.xml``):::
    
    TODO

To verify that a stylesheet has been installed in the ``portal_css`` tool
(e.g. via ``cssregistry.xml``)::

    TODO

To verify that a JavaScript resource has been installed in the
``portal_javascripts`` tool (e.g. via ``jsregistry.xml``)::

    TODO

To verify that a new role has been added (e.g. via ``rolemap.xml``)::

    TODO

To verify that a permission has been granted to a given set of roles (e.g. via
``rolemap.xml``)::

    TODO

Traversal
---------

To traverse to a view, page template or other resource::

    TODO

This performs an explicit security check. If you don't want that, you can
use::
    
    TODO

Note that this traversal will not take ``IPublishTraverse`` adapters into
account.

To look up a view manually::

    TODO

To simulate an ``IPublishTraverse`` adapter call::

    TODO

Invoking views
--------------

To obtain an instance of a view or template::

    TODO

To simulate a form submission or query string parameters::

    TODO

To invoke a view and obtain the results::

    TOOD

To inspect the state of the request::

    TODO

To inspect response headers::

    TODO

Simulating browser interaction
------------------------------

End-to-end functional tests can use `zope.testbrowser`_ to simulate user
interaction. This acts as a web browser, connecting to Zope via a special
channel, making requests and obtaining responses.

  **Note:** zope.testbrowser runs entirely in Python, and does not simulate
  a JavaScript engine.

Note that to use ``zope.testbrowser``, you need to use one of the functional
testing layers, e.g. ``PLONE_FUNCTIONAL_TESTING``. If you want to create some
initial content, you can do so either in a layer, or in the test before
invoking the test browser client. In the latter case, you need to commit
the transaction before it becomes available, e.g.::

    # Make some changes
    helper.setRoles(portal, TEST_USER_NAME, ['Manager'])
    portal.invokeFactory('Folder', 'f1', title=u"Folder 1")
    helper.setRoles(portal, TEST_USER_NAME, ['Member'])
    
    # Commit so that the test browser sees these changes
    import transaction
    transaction.commit()

To obtain a new test browser client::

    TODO

To open a given URL::

    TODO

To inspect the response::

    TODO

To inspect headers::

    TODO

To inspect the error log (in case of an unexpected error)::

    TODO

To follow a link::
    
    TODO

To set a form control value::

    TODO

To submit a form by clicking a button::

    TODO

To simulate HTTP BASIC authentication (i.e. remain logged in for all
requests):

    TODO

To simulate logging in via the login form:

    TODO

To simulate logging out::

    TODO

Debugging tip: to save the current response to an HTML file::

    TODO
    
You can now open this file and use tools like Firebug to inspect the structure
of the page.

Please see the `zope.testbrowser`_ documentation for more examples.

Comparison with ZopeTestCase/PloneTestCase
==========================================

`plone.testing`_ and ``plone.app.testing`` have in part evolved from
``ZopeTestCase``, which ships with Zope 2 in the ``Testing`` package, and
`Products.PloneTestCase`_, which ships with Plone and is used by Plone itself
as well as numerous add-on products.

If you are familiar with ``ZopeTestCase`` and ``PloneTestCase``, the concepts
of these package should be familiar to you. However, there are some important
differences to bear in mind.

* ``plone.testing`` and ``plone.app.testing`` are unburdened by the legacy
  support that ``ZopeTestCase`` and ``PloneTestCase`` have to include. This
  makes them smaller and easier to understand and maintain.

* Conversely, ``plone.testing`` only works with Python 2.6 and Zope 2.12 and
  later. ``plone.app.testing`` only works with Plone 4 and later. If you need
  to write tests that run against older versions of Plone, you'll need to use
  ``PloneTestCase``.

* ``ZopeTestCase``/``PloneTestCase`` were written before layers were available
  as a setup mechanism. ``plone.testing`` is very layer-oriented.

* ``PloneTestCase`` provides a base class, also called ``PloneTestCase``,
  which you must use, as it performs setup and tear-down. ``plone.testing``
  moves shared state to layers and layer resources, and does not impose any
  particular base class for tests. This does sometimes mean a little more
  typing (e.g. ``self.layer['portal']`` vs. ``self.portal``), but it makes
  it much easier to control and re-use test fixtures. It also makes your 
  test code simpler and more explicit.

* ``ZopeTestCase`` has an ``installProduct()`` function and a corresponding
  ``instalPackage()`` function. `plone.testing`_ has only an
  ``installProduct()``, which can configure any kind of Zope 2 product (i.e.
  packages in the ``Products.*`` namespace, old-style products in a special
  ``Products`` folder, or packages in any namespace that have had their ZCML
  loaded and which include a ``<five:registerPackage />`` directive in their
  configuration). Note that you must pass a full dotted name to this function,
  even for "old-style" products in the ``Products.*`` namespace, e.g.
  ``Products.LinguaPlone`` instead of ``LinguaPlone``.

* On setup, ``PloneTestCase`` will load Zope 2's default ``site.zcml``. This
  in turn will load all ZCML for all packages in the ``Products.*`` namespace.
  ``plone.testing`` does not do this (and you are strongly encouraged from
  doing it yourself), because it is easy to accidentally include packages in
  your fixture that you didn't intend to be there (and which can actually
  change the fixture substantially). You should load your package's ZCML
  explicitly. See the `plone.testing`_ documentation for details.

* When using ``PloneTestCase``, any package that has been loaded onto
  ``sys.path`` and which defines the ``z3c.autoinclude.plugin:plone`` entry
  point will be loaded via `z3c.autoinclude`_'s plugin mechanism. This loading
  is explicitly disabled, for the same reasons that the ``Products.*`` auto-
  loading is. You should load your packages' configuration explicitly.

.. _plone.testing: http://pypi.python.org/pypi/plone.testing
.. _zope.testing: http://pypi.python.org/pypi/zope.testing
.. _z3c.autoinclude: http://pypi.python.org/pypi/z3c.autoinclude
.. _zope.testbrowser: http://pypi.python.org/pypi/zope.testbrowser
.. _Products.PloneTestCase: http://pypi.python.org/pypi/Products.PloneTestCase