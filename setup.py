from setuptools import setup, find_packages

version = '4.2'

tests_require = ['Products.CMFCore',
                 'Products.PluggableAuthService',
                 'selenium',
                 'transaction',
                 'unittest2',
                 'zope.interface',
                 'zope.publisher',
                 ]

setup(name='plone.app.testing',
      version=version,
      description="Testing tools for Plone-the-application, based on plone.testing.",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        ],
      keywords='',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/plone.app.testing',
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
      },
      )
