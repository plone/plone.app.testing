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

1. Remove any GenericSetup profiles that were loaded during setup from the
   global registry.

2. Pop the global component registry to unregister components loaded via ZCML.

3. Pop the ``DemoStorage`` to undo any persistent changes.

If you have made other changes on setup that are not covered by this broad
tear-down, you'll also want to tear those down explicitly here.

Stacking a demo storage and component registry and snapshotting the
GenericSetup profile registry is the easiest way to avoid fixtures bleeding
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