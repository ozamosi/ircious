from ircious.ircious_app.utils import *
from ircious.ircious_app import utils
from ircious.ircious_app.models import LinkObj

from django.test import TestCase
from django.test.client import Client

class TestEditDelete(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        u = User()
        u.save()
        n = Nick(nickname="ozamosi", user=u)
        n.save()
        inw = IrcNetwork()
        inw.save()
        ic = IrcChannel(network=inw, name="#ircious")
        ic.save()
        lo = LinkObj(slug='test-one-that-actually-does-exist', url='http://example.com', title='Test')
        lo.save()
        lp = LinkPost(comment="Test", user=u, link=lo, channel=ic)
        lp.save()
        lo.last_post = lp
        lo.save()

    def test_edit(self):
        lp = LinkPost.objects.all()[0]
        response = self.client.get('/%i/edit/' % lp.pk)
        self.failUnlessEqual(response.status_code, 200)

    def test_delet(self):
        lp = LinkPost.objects.all()[0]
        response = self.client.get('/%i/delete/' % lp.pk)
        self.failUnlessEqual(response.status_code, 200)

class TestAllUrlWorks(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        u = User()
        u.save()
        n = Nick(nickname="ozamosi", user=u)
        n.save()
        inw = IrcNetwork()
        inw.save()
        ic = IrcChannel(network=inw, name="#ircious")
        ic.save()
        lo = LinkObj(slug='test-one-that-actually-does-exist', url='http://example.com', title='Test')
        lo.save()
        lp = LinkPost(comment="Test", user=u, link=lo, channel=ic)
        lp.save()
        lo.last_post = lp
        lo.save()

    def do_test(self, path, code):
        response = self.client.get(path)
        self.failUnlessEqual(response.status_code, code)

    def test_start(self):
        self.do_test('/', 200)
        self.do_test('/feed/', 200)

    def test_user(self):
        self.do_test('/user/ozamosi/', 200)
        self.do_test('/user/ozamosi/feed/', 200)
        self.do_test('/user/not-ozamosi/', 404)
        self.do_test('/user/not-ozamosi/feed/', 404)

    def test_channel(self):
        self.do_test('/channel/ircious/', 200)
        self.do_test('/channel/ircious/feed/', 200)
        self.do_test('/channel/not-ircious/', 404)
        self.do_test('/channel/not-ircious/feed/', 404)

    def test_slug(self):
        self.do_test('/slug/test-one-that-doesnt-really-exist/feed/', 404)
        self.do_test('/slug/test-one-that-doesnt-really-exist/', 404)
        self.do_test('/slug/test-one-that-actually-does-exist/feed/', 200)
        self.do_test('/slug/test-one-that-actually-does-exist/', 200)

__test__ = {
    'addOidUser': utils.addOidUser,
    'addPost': utils.addPost,
    'getUserWithNick': utils.getUserWithNick,
    'getYoutubeScreenshotUrl': utils.getYoutubeScreenshotUrl,
}

if __name__ == "__main__":
    import doctest
    doctest.testmod()
