import unittest
import re
from StringIO import StringIO

import twill

from application import app
import secrets

TWILLHOST = 'testserver'

def url_for_twill(relative_url):
    return 'http://%s%s' % (TWILLHOST, relative_url)

class TwillTestCase(unittest.TestCase):
    def setUp(self):
        twill.set_output(StringIO())
        twill.commands.clear_cookies()
        twill.add_wsgi_intercept(TWILLHOST, 80, lambda:app)
        self.browser = twill.get_browser()
    
    def tearDown(self):
        twill.commands.reset_output()

class OauthTestCase(TwillTestCase):
    def test_authorize(self):
        """User can authorize our app"""
        self.browser.go(url_for_twill('/'))
        twill.commands.formvalue(1, 'search', 'test')
        self.browser.submit()
        login_url = 'https://www.google.com/accounts/ServiceLogin'
        self.assertTrue(self.browser.get_url().startswith(login_url))
    
        # login to Google account
        twill.commands.formvalue(1, 'Passwd', secrets.TEST_GOOGLE_PASSWORD)
        twill.commands.formvalue(1, 'Email', secrets.TEST_GOOGLE_EMAIL)
        self.browser.submit()
        auth_url = 'https://www.google.com/accounts/OAuthAuthorizeToken'
        self.assertTrue(self.browser.get_url().startswith(auth_url))
        
        # Google redirects to our app
        self.browser.submit('allow')
        self.assertEqual(self.browser.get_url(), url_for_twill('/check/'))
        
class AppTestCase(unittest.TestCase):

    browser = None
    def setUp(self):
        """Setup an authorized user so we can test app functionality"""
        # Handles setting the state once for the all tests in this class
        # http://stackoverflow.com/questions/402483/caching-result-of-setup-using-python-unittest/402492#402492
        if not self.browser:
            twill.set_output(StringIO())
            twill.commands.clear_cookies()
            twill.add_wsgi_intercept(TWILLHOST, 80, lambda:app)
            self.__class__.browser = twill.get_browser()
            # authorize user against Gmail for our app
            self.__class__.browser.go(url_for_twill('/'))
            twill.commands.formvalue(1, 'search', 'test')
            self.__class__.browser.submit()
            twill.commands.formvalue(1, 'Passwd', secrets.TEST_GOOGLE_PASSWORD)
            twill.commands.formvalue(1, 'Email', secrets.TEST_GOOGLE_EMAIL)
            self.__class__.browser.submit()
            self.__class__.browser.submit('allow')
            
    def search_results(self, search_val):
        self.browser.go(url_for_twill('/check/'))
        twill.commands.formvalue(1, 'search', search_val)
        self.browser.submit()
        return re.findall(search_val, self.browser.get_html())
        
    def test_search_name(self):
        """Search by email name"""
        finds = self.search_results("Gmail Team")
        # expects 3 in inbox + 1 in search field
        self.assertEqual(len(finds), 4)
        
    def test_search_results(self):
        """Search by email address"""
        finds = self.search_results("mail-noreply@google.com")
        # expects 3 in inbox + 1 in search field
        self.assertEqual(len(finds), 4)
    
    def test_failed_search(self):
        """Search for something that isn't there"""
        finds = self.search_results("antidisestablishmentarianism")
        # expects 0 in inbox + 1 in search field
        self.assertEqual(len(finds), 1)


if __name__ == '__main__':
    unittest.main()