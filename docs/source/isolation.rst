Test Isolation is hard
======================

At the moment, it is not possible to just run all tests at once.
Therfore we have an alltests script that groups tests together.

You may wonder, why and which tests need to be separated.

plone.app.testing vs ZopeTestCase
---------------------------------

plone.app.testing goes at great lengths to isolate tests.
The zope component architecture does not provide easy ways to isolate and revert changes.

So, I hear you saying let us monkey patch the zope component architecture.

That is what plone.app.testing and ZopeTestCase also thought.

They monkey patch in different ways.
The practical result is, that the first time, a ZopeTestCase runs, test isolation is broken and suddenly every test runs in the same demo storage while the teardowns, tear down a totally unrelated stacked demo storage.

That means that the second test with plone.app.testing will see the changes from the first test.

If you create tests with both plone.app.testing and ZopeTestCase, they can have random failures depending of ordering.

anything vs MockTestCase
------------------------
MockTestCase has integration functionality for using mockers.
You can easily register your mocks so that they get removed after the test.
Thing is, something patches something in such a way, that unregistering mocks stop working.
Worse, the stack is somehow also gone so that it is impossible to figure out via pdb, what is failing.
