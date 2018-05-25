# -*- coding: utf-8 -*-
"""Backwards-compatibility test class for PloneTestCase."""

from AccessControl import getSecurityManager
from plone.app import testing
from plone.testing import z2
from Products.CMFPlone.utils import _createObjectByType
from Testing.ZopeTestCase.functional import Functional

import transaction
import unittest

try:
    import Products.Archetypes
    HAVE_AT = True
except ImportError:
    HAVE_AT = False


def _createMemberarea(portal, user_id):
    mtool = portal.portal_membership
    members = mtool.getMembersFolder()
    if members is None:
        _createObjectByType('Folder', portal, id='Members')
    if not mtool.getMemberareaCreationFlag():
        mtool.setMemberareaCreationFlag()
    mtool.createMemberArea(user_id)
    if mtool.getMemberareaCreationFlag():
        mtool.setMemberareaCreationFlag()


class PloneTestCaseFixture(testing.PloneSandboxLayer):

    defaultBases = (testing.PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        if HAVE_AT:
            import Products.ATContentTypes
            self.loadZCML(package=Products.ATContentTypes)

            z2.installProduct(app, 'Products.Archetypes')
            z2.installProduct(app, 'Products.ATContentTypes')
            z2.installProduct(app, 'plone.app.blob')
            z2.installProduct(app, 'plone.app.collection')
        else:
            import plone.app.contenttypes
            self.loadZCML(package=plone.app.contenttypes)
            z2.installProduct(app, 'plone.app.contenttypes')


    def setUpPloneSite(self, portal):
        # restore default workflow
        testing.applyProfile(portal, 'Products.CMFPlone:testfixture')

        # add default content
        if HAVE_AT:
            testing.applyProfile(portal, 'Products.ATContentTypes:content')
        else:
            testing.applyProfile(portal, 'plone.app.contenttypes:default')

        # add home folder for default test user
        _createMemberarea(portal, testing.TEST_USER_ID)

    def tearDownZope(self, app):
        if HAVE_AT:
            z2.uninstallProduct(app, 'plone.app.collection')
            z2.uninstallProduct(app, 'plone.app.blob')
            z2.uninstallProduct(app, 'Products.ATContentTypes')
            z2.uninstallProduct(app, 'Products.Archetypes')
        else:
            z2.uninstallProduct(app, 'plone.app.contenttypes')


PTC_FIXTURE = PloneTestCaseFixture()
PTC_FUNCTIONAL_TESTING = testing.FunctionalTesting(
    bases=(PTC_FIXTURE,), name='PloneTestCase:Functional')


class PloneTestCase(Functional, unittest.TestCase):

    layer = PTC_FUNCTIONAL_TESTING

    def setUp(self):
        """Set up before each test."""
        self.beforeSetUp()
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.folder = self.portal.portal_membership.getHomeFolder(
            testing.TEST_USER_ID)
        transaction.commit()
        self.afterSetUp()

    def beforeSetUp(self):
        """Hook to do setup before the portal is created."""
        pass

    def afterSetUp(self):
        """Hook to do setup after the portal is created."""

    def tearDown(self):
        """Tear down after each test."""
        self.beforeTearDown()
        transaction.abort()
        super(PloneTestCase, self).tearDown()
        self.afterTearDown()

    def beforeTearDown(self):
        """Hook to do teardown before the portal is removed."""

    def afterTearDown(self):
        """Hook to do teardown after the portal is removed."""

    def setRoles(self, roles, name=testing.TEST_USER_ID):
        """Set the effective roles of a user."""
        testing.setRoles(self.portal, name, roles)

    def setGroups(self, groups, name=testing.TEST_USER_ID):
        '''Changes the user's groups.'''
        uf = self.portal['acl_users']
        uf.userSetGroups(name, list(groups))
        user = getSecurityManager().getUser()
        if name == user.getId():
            self.login(user.getUserName())

    def setPermissions(self, permissions, role='Member'):
        """Changes the permissions assigned to role."""
        self.portal.manage_role(role, list(permissions))

    def login(self, userName=testing.TEST_USER_NAME):
        """Log in to the portal as the given user."""
        testing.login(self.portal, userName)

    def loginAsPortalOwner(self, userName=testing.SITE_OWNER_NAME):
        """Log in to the portal as the user who created it."""
        z2.login(self.app['acl_users'], userName)

    def logout(self):
        """Log out, i.e. become anonymous."""
        testing.logout()

    def createMemberarea(self, name):
        """Create a minimal memberarea."""
        _createMemberarea(self.portal, name)
