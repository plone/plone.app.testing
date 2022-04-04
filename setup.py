# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

import os


version = '7.0.0a2'

tests_require = [
    'plone.testing[test]',
    'Products.CMFCore',
    'Products.CMFPlacefulWorkflow',
    'Products.CMFPlone',
    'Products.PluggableAuthService',
    'selenium',
    'transaction',
    'zope.interface',
    'zope.publisher',
    'zope.testing',
    'zope.testrunner',
    # XXX unspecified dependency of plone.app.upgrade XXX
    # 'Products.ATContentTypes',
]

robot_require = [
    'robotsuite>=1.4.0',
    'robotframework-selenium2library',
    'decorator',
    'selenium',
]


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


long_description = \
    read('docs', 'README.rst') + \
    '\n\n' +\
    read('CHANGES.rst')


setup(
    name='plone.app.testing',
    version=version,
    description="Testing tools for Plone-the-application, based on plone.testing.",  # NOQA: E501
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: Core",
        "Framework :: Zope :: 4",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    keywords='plone tests',
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://pypi.org/project/plone.app.testing',
    license='GPL version 2',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['plone', 'plone.app'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'six',
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
        'Zope',
    ],
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
        'robot': robot_require,
    },
)
