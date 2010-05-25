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
manage test set-up and tear-down differently.

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
| Resources: | ``portal`` (test set-up only)                    |
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
| Resources: | ``portal`` (test set-up only)                    |
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
| Resources: | ``portal`` (test set-up only)                    |
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
| Resources: | ``portal`` (test set-up only)                    |
+------------+--------------------------------------------------+

This is layer is intended for functional testing using a live, running HTTP
server, e.g. using Selenium or Windmill.

See the description of the ``z2.FTP_SERVER`` layer in `plone.testing`_
for details.

Helper functions
================

User management
---------------

Product and profile installation
--------------------------------

Component architecture sandboxing
---------------------------------

Example - creating a custom layer
=================================

Common test patterns
====================

Comparison with ZopeTestCase/PloneTestCase
==========================================

.. _plone.testing: http://pypi.python.org/pypi/plone.testing
.. _zope.testing: http://pypi.python.org/pypi/zope.testing
.. _z3c.autoinclude: http://pypi.python.org/pypi/z3c.autoinclude
.. _zope.testbrowser: http://pypi.python.org/pypi/zope.testbrowser
