from setuptools import setup, find_packages
import os

version = '1.0a1'

setup(name='plone.app.testing',
      version=version,
      description="Testing itools for Plone-the-application, based on plone.testing",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.configuration',
          'zope.dottedname',
          'zope.site',
          'five.localsitemanager',
          'plone.testing [zca,zodb,z2]',
          'Plone',
      ],
      extras_require = {
        'test': [
                'Products.GenericSetup',
                'Products.PluggableAuthService',
                'ZODB3',
                'Zope2',
            ],
      },
      entry_points="""
      """,
      )
