from pathlib import Path
from setuptools import find_packages
from setuptools import setup


version = "7.1.2"

long_description = (
    f"{(Path('docs') / 'README.rst').read_text()}\n"
    f"{Path('CHANGES.rst').read_text()}"
)

tests_require = [
    "plone.testing[test]",
    "Products.CMFPlone",
    "Products.PluggableAuthService",
    "requests",
    "transaction",
    "zope.interface",
    "zope.testing",
    "zope.testrunner",
    # XXX unspecified dependency of plone.app.upgrade XXX
    # 'Products.ATContentTypes',
]

robot_require = [
    "robotsuite>=1.4.0",
    "robotframework-selenium2library",
    "decorator",
    "selenium",
]

setup(
    name="plone.app.testing",
    version=version,
    description="Testing tools for Plone-the-application, based on plone.testing.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    # Get more strings from
    # https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: 6.1",
        "Framework :: Plone :: Core",
        "Framework :: Zope :: 4",
        "Framework :: Zope :: 5",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    keywords="plone tests",
    author="Plone Foundation",
    author_email="plone-developers@lists.sourceforge.net",
    url="https://pypi.org/project/plone.app.testing",
    license="GPL version 2",
    packages=find_packages("src"),
    package_dir={"": "src"},
    namespace_packages=["plone", "plone.app"],
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[
        "Products.CMFPlone",
        "Products.GenericSetup",
        "Products.MailHost",
        "Products.PluggableAuthService",
        "Zope",
        "persistent",
        "plone.app.contenttypes",
        "plone.dexterity",
        "plone.memoize",
        "plone.registry",
        "plone.testing [zca,security,zodb]",
        "setuptools",
        "zope.configuration",
        "zope.component",
        "zope.dottedname",
        "zope.testing",
    ],
    extras_require={
        "test": tests_require,
        "robot": robot_require,
    },
)
