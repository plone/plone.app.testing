Views
=====

Test view registration
----------------------

Test if view has been properly registered::

    def test_delete_view_registered(self):
        try:
            getMultiAdapter(
                (self.portal.mi.se.tc, self.request),
                name="delete"
            )
        except:
            self.fail("Delete view is not registered properly.")


Test with getMultiAdapter
-------------------------

Test::

    def test_view_is_registered(self):
        # Get the view
        view = getMultiAdapter((self.portal, self.portal.REQUEST), name="create-user")
        # Call the view
        self.assertTrue(view())


Test with restrictedTraverse
----------------------------

Test::

    def test_view_is_registered(self):
        view = self.portal.restrictedTraverse('@@list-products')
        self.assertTrue(view)
        self.assertEqual(view(), 'ListProductsView')

Test view with parameter
------------------------

Test::

    def test_autocomplete_tags_view_registered(self):
        self.request.set('term', 'foo')
        view = getMultiAdapter((self.portal, self.request),
                               name="autocomplete-tags")
        self.assertTrue(view())


Test with restrictedTraverse and parameter
------------------------------------------

Test::

    def test_view_with_restrictedTraverse_and_params(self):
        view = self.context.restrictedTraverse("comment-statistics-batch")
        view(query, base_number * i, base_number * (i + 1) - 1)


Test if view is protected
-------------------------

Test::

    def test_view_is_protected(self):
        from AccessControl import Unauthorized
        self.logout()
        self.assertRaises(Unauthorized,
                          self.portal.restrictedTraverse,
                          '@@deploymentmanager')

Test if object exists in folder
-------------------------------

Test::

    def test_object_in_folder(self):
        self.assertFalse('yoda' in self.portal.objectIds())

Test Redirect
-------------

Test::

    def test_component_view(self):
        self.portal.mi.sec.invokeFactory(
            "TextComponent",
            id="tx",
            title="Text Component 1",
        )
        view = getMultiAdapter(
            (self.portal.mi.sec.tx, self.request),
            name="view"
        )

        view()

        self.assertEqual(
            self.request.response.headers['location'],
            'http://nohost/plone/mi/sec'
        )

Test View HTML Output
=====================

Test::

    from lxml import html
    output = html.fromstring(view())
    self.assertEqual(len(output.xpath("/html/body/div")), 1)


Troubleshooting
===============

KeyError: 'ACTUAL_URL'::

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']
        self.request.set('URL', self.folder.absolute_url())
        self.request.set('ACTUAL_URL', self.folder.absolute_url())

    def test_view(self):
        view = self.collection.restrictedTraverse('@@RSS')
        self.assertTrue(view())
        self.assertEqual(view.request.response.status, 200)


ComponentLookupError
--------------------

If a view can not be looked up on a particular context, Plone will raise a
ComponentLookupError (because views are multi-adapters), e.g.::

    ComponentLookupError: ((<PloneSite at /plone>, <HTTPRequest, URL=http://nohost/plone>), <InterfaceClass zope.interface.Interface>, 'recipes')::

This can be solved for instance by providing a browser layer that has been
missing::

    def setUp(self):
        self.request = self.layer['request']
        from zope.interface import directlyProvides
        directlyProvides(self.request, IMyCompanyContenttypes)
        ...


AttributeError: @@plone_portal_state
------------------------------------



Test View Methods
=================

Test::

    def test_method_sections(self):
        self.portal.mi.invokeFactory("Section", id="s1", title="Section 1")
        self.portal.mi.invokeFactory("Section", id="s2", title="Section 2")
        view = getMultiAdapter(
            (self.portal.mi, self.request),
            name="view"
        )

        self.assertEqual(len(view.sections()), 2)
        self.assertEqual(
            [x.title for x in view.sections()]
            [u'Section 1', u'Section 2']
        )


View Status Messages
--------------------

Test::

    def test_delete_comments_sets_status_message(self):
        view = getMultiAdapter(
            (self.portal.mi.se.tc, self.request),
            name="delete"
        )

        view()

        self.assertEqual(
            IStatusMessage(self.request).show()[0].message,
            u'Item deleted'
        )

View Class::

    class DeleteComponent(BrowserView):

        def __call__(self):
            section = aq_parent(self.context)
            section.manage_delObjects([self.context.id])
            IStatusMessage(self.context.REQUEST).addStatusMessage(
                _("Item deleted"),
                type="info"
            )
            self.request.response.redirect(section.absolute_url())

