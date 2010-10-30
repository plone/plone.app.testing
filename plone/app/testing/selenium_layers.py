import os
import transaction

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import FunctionalTesting
from plone.app.testing.layers import PLONE_FIXTURE
from plone.testing import z2


class SeleniumLayer(PloneSandboxLayer):
    defaultBases = (z2.ZSERVER_FIXTURE, PLONE_FIXTURE)

    def setUpPloneSite(self, portal):
        # Start up Selenium
        driver = os.environ.get('SELENIUM_DRIVER', 'firefox')
        webdriver = __import__(
            'selenium.%s.webdriver' % driver, fromlist=['WebDriver'])
        self['selenium'] = webdriver.WebDriver()

    def tearDownPloneSite(self, portal):
        self['selenium'].quit()
        del self['selenium']

SELENIUM_FIXTURE = SeleniumLayer()
SELENIUM_TESTING = FunctionalTesting(
    bases=(SELENIUM_FIXTURE,), name="SeleniumTesting:Functional")


def open(selenium, url):
    # ensure we have a clean starting point
    transaction.commit()
    selenium.get(url)
