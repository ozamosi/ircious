from ircious.ircious_app.utils import *
from ircious.ircious_app import utils
from ircious.ircious_app.models import LinkObj

from django.test import TestCase
from django.test.client import Client

class TestModifyingOperationsUnsatisfyingly(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        u = User()
        u.save()
        n = Nick(nickname="ozamosi", user=u)
        n.save()
        inw = IrcNetwork()
        inw.save()
        ic = IrcChannel(network=inw, name="#ircious", requested_by=u)
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

    def test_delete(self):
        lp = LinkPost.objects.all()[0]
        response = self.client.get('/%i/delete/' % lp.pk)
        self.failUnlessEqual(response.status_code, 200)

    def test_addfav(self):
        lp = LinkPost.objects.all()[0]
        response = self.client.get('/%i/favourite/' % lp.pk)
        self.failUnlessEqual(response.status_code, 200)


class TestAddChannel(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        u = User()
        u.save()
        n = Nick(nickname="ozamosi", user=u)
        n.save()
        inw = IrcNetwork()
        inw.save()
        ic = IrcChannel(network=inw, name="#ircious", requested_by=u)
        ic.save()
        lo = LinkObj(slug='test-one-that-actually-does-exist', url='http://example.com', title='Test')
        lo.save()
        lp = LinkPost(comment="Test", user=u, link=lo, channel=ic)
        lp.save()
        lo.last_post = lp
        lo.save()
    def test_post_add_channel(self):
        response = self.client.post('/add_channel/', {'channel': 'blubb', 'network': 'apa', 'nick': 'gao'})
        self.assertFormError(response, 'form', 'nick', 'That is not an existing user')
        
        response = self.client.post('/add_channel/', {'channel': 'blubb', 'network': 'apa', 'nick': 'ozamosi'})
        self.assertRedirects(response, 'http://testserver/')
        channel = IrcChannel.objects.filter(name="#blubb")
        self.failUnlessEqual(channel.count(), 1)
        channel = channel[0]
        self.failUnlessEqual(channel.network.name, "apa")
        self.failUnlessEqual(channel.requested_by.nick_set.get().nickname, "ozamosi")
        self.failUnlessEqual(channel.active, False)

    def test_add_channel(self):
        response = self.client.get('/add_channel/')
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
        ic = IrcChannel(network=inw, name="#ircious", requested_by=u)
        ic.save()
        lo = LinkObj(slug='test-one-that-actually-does-exist', url='http://example.com', title='Test')
        lo.save()
        lp = LinkPost(comment="Test", user=u, link=lo, channel=ic)
        lp.save()
        lo.last_post = lp
        lo.save()

    def do_test(self, path, code):
        def test(path, code):
            response = self.client.get(path)
            self.failUnlessEqual(response.status_code, code)
        test(path, code)
        test(path+'feed/', code)
        test(path+'0/', code)
        test(path+'feed/0/', code)


    def test_start(self):
        self.do_test('/', 200)

    def test_user(self):
        self.do_test('/user/ozamosi/', 200)
        self.do_test('/user/not-ozamosi/', 404)

    def test_user_favourites(self):
        self.do_test('/user/ozamosi/favourites/', 200)
        self.do_test('/user/not-ozamosi/favourites/', 404)

    def test_channel(self):
        self.do_test('/channel/ircious/', 200)
        self.do_test('/channel/not-ircious/', 404)

    def test_slug(self):
        self.do_test('/slug/test-one-that-actually-does-exist/', 200)
        self.do_test('/slug/test-one-that-doesnt-really-exist/', 404)

__test__ = {
    'addOidUser': utils.addOidUser,
    'addPost': utils.addPost,
    'getUserWithNick': utils.getUserWithNick,
    'getYoutubeScreenshotUrl': utils.getYoutubeScreenshotUrl,
    'getTitleFromUrl': utils.getTitleFromUrl,
    'getFlickrScreenshotUrl': utils.getFlickrScreenshotUrl,
}

if __name__ == "__main__":
    import doctest
    doctest.testmod()
