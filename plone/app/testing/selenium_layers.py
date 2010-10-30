import os
import transaction

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import FunctionalTesting
from plone.app.testing.layers import PLONE_FIXTURE
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from plone.testing import z2


class SeleniumLayer(PloneSandboxLayer):
    defaultBases = (z2.ZSERVER_FIXTURE, PLONE_FIXTURE)

    def setUpPloneSite(self, portal):
        # Start up Selenium
        driver = os.environ.get('SELENIUM_DRIVER', '') or 'firefox'
        webdriver = __import__(
            'selenium.%s.webdriver' % driver, fromlist=['WebDriver'])
        args = [arg.strip() for arg in
                os.environ.get('SELENIUM_ARGS', '').split()
                if arg.strip()]
        self['selenium'] = webdriver.WebDriver(*args)

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

def login(selenium, portal, username=False, password=False):
    
    if not username:
        username = TEST_USER_NAME
    if not password:
        password = TEST_USER_PASSWORD
    
    selenium.get(portal.absolute_url() + '/login_form')
    selenium.find_element_by_name('__ac_name').send_keys(username)
    selenium.find_element_by_name('__ac_password').send_keys(password)
    selenium.find_element_by_name('submit').click()