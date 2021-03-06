from django.conf.urls.defaults import *

urlpatterns = patterns('ircious.ircious_app.views',
    (r'^((?P<page>\d+)/)?$', 'list'),
    (r'^feed/((?P<page>\d+)/)?$', 'list', {'feed': True}),

    (r'^error/(?P<error>.+)/$', 'list'),

    (r'^user/(?P<username>[^/]+)/((?P<page>\d+)/)?$', 'list'),
    (r'^user/(?P<username>[^/]+)/feed/((?P<page>\d+)/)?$', 'list', {'feed': True}),

    (r'^user/(?P<username>[^/]+)/favourites/((?P<page>\d+)/)?$', 'favourites'),
    (r'^user/(?P<username>[^/]+)/favourites/feed/((?P<page>\d+)/)?$', 'favourites', {'feed': True}),

    (r'^channel/(?P<channel>[^/]+)/((?P<page>\d+)/)?$', 'list'),
    (r'^channel/(?P<channel>[^/]+)/feed/((?P<page>\d+)/)?$', 'list', {'feed': True}),

    (r'^slug/(?P<slug>[a-z0-9-]+)/$', 'showlink'), #Needed to not confuse reverse()
    (r'^slug/(?P<slug>[a-z0-9-]+)/(?P<page>\d+)/$', 'showlink'),
    (r'^slug/(?P<slug>[a-z0-9-]+)/feed/((?P<page>\d+)/)?$', 'showlink', {'feed': True}),

    (r'^(?P<id>[0-9]+)/edit/$', 'edit_post',),
    (r'^(?P<id>[0-9]+)/delete/$', 'delete_post',),
    (r'^add_channel/$', 'add_channel',),

    (r'^(?P<id>[0-9]+)/favourite/$', 'add_favlist',),

    (r'^search/(?P<searchstring>.*)/((?P<page>\d+)/)?$', 'search'),
    (r'^search/(?P<searchstring>.*)/feed/((?P<page>\d+)/)?$', 'search', {'feed': True}),
)
