from ircious.ircious_app.utils import *
from ircious.ircious_app import utils
from django.test import TestCase
from django.test.client import Client

class TestAllUrlWorks(TestCase):
    def test_start(self):
        response = self.client.get('/')
        self.failUnlessEqual(response.status_code, 200)

    def test_user(self):
        response = self.client.get('/user/ozamosi/') 
        self.failUnlessEqual(response.status_code, 200)

    def test_channel(self):
        response = self.client.get('/channel/ircious/')
        self.failUnlessEqual(response.status_code, 200)


__test__ = {
    'addOidUser': utils.addOidUser,
    'addPost': utils.addPost,
    'getUserWithNick': utils.getUserWithNick,
    'getYoutubeScreenshotUrl': utils.getYoutubeScreenshotUrl,
}

if __name__ == "__main__":
    import doctest
    doctest.testmod()
