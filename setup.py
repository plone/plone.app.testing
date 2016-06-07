from setuptools import setup, find_packages
import os

version = '5.0.2'

tests_require = ['Products.CMFCore',
                 'Products.CMFPlone',
                 'Products.PluggableAuthService',
                 'Products.ATContentTypes',  # XXX unspecified dependency of plone.app.upgrade XXX
                 'Products.CMFPlacefulWorkflow',
                 'selenium',
                 'transaction',
                 'zope.interface',
                 'zope.publisher',
                 'zope.testrunner',
                 ]

robot_require = ['robotsuite>=1.4.0',
                 'robotframework-selenium2library',
                 'decorator',
                 'selenium']

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = \
    read('docs', 'source','README.rst') + \
    '\n\n' +\
    read('CHANGES.rst')

setup(
    name='plone.app.testing',
    version=version,
    description="Testing tools for Plone-the-application, based on plone.testing.",
    long_description=long_description,
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 5.0",
        "Framework :: Zope2",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    keywords='',
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
