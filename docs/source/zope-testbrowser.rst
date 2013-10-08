Simulating browser interaction with zope.testbrowser
====================================================

Input
-----

todo

Text Area
---------

HTML::

  <textarea name="form.widgets.mytext"></textarea>

Test::

  self.browser.getControl(name='form.widgets.mytext').value = '<p>Lorem Ipsum</p>'

Radio Buttons
-------------

  self.browser.getControl(name='form.widgets.city:list').value = ['Berlin']

Checkboxes
----------

HTML::

  <input type="checkbox"
         value="selected"
         checked="checked"
         name="form.widgets.city:list">

Test::

  self.browser.getControl(
      name="form.widgets.city:list"
  ).value = ['checked']


Select
------

todo


Links
-----

  self.browser.getLink('Publish').click()


Buttons
-------

  self.browser.getControl('Save').click()


Image Upload
------------

  self.browser.getLink('Image').click()
  self.browser.getControl(name='form.widgets.title')\
    .value = "My image"
  self.browser.getControl(name='form.widgets.description')\
    .value = "This is my image."
  image_path = os.path.join(os.path.dirname(__file__), "image.png")
  image_ctl = self.browser.getControl(name='form.widgets.image')
  image_ctl.add_file(open(image_path), 'image/png', 'image.png')
  self.browser.getControl('Save').click()

File Upload
-----------

todo
