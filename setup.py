from setuptools import setup, find_packages

version = '4.2.6'

tests_require = ['Products.CMFCore',
                 'Products.CMFPlone',
                 'Products.PluggableAuthService',
                 'selenium',
                 'transaction',
                 'unittest2',
                 'zope.interface',
                 'zope.publisher',
                 ]

robot_require = ['robotsuite',
                 'robotframework-selenium2library',
                 'decorator',
                 'selenium']

setup(name='plone.app.testing',
      version=version,
      description="Testing tools for Plone-the-application, based on plone.testing.",
      long_description=open("README.rst").read() + "\n" +
                       open("CHANGES.rst").read(),
      classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        ],
      keywords='plone tests',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='https://pypi.python.org/pypi/plone.app.testing',
      license='GPL version 2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.configuration',
          'zope.component',
          'zope.dottedname',
          'zope.site',
          'zope.testing',
          'five.localsitemanager',
          'plone.memoize',
          'plone.testing [zca,security,zodb,z2]',
          # 'Acquisition', # Zope 2.13+
          # 'AccessControl', # Zope 2.13+
          'Products.CMFPlone',
          'Products.GenericSetup',
          'Zope2',
      ],
      tests_require=tests_require,
      extras_require={
        'test': tests_require,
        'robot': robot_require,
      },
      )
