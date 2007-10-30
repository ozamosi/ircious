from django.conf.urls.defaults import *

urlpatterns = patterns('ircious.django_openidconsumer.views',
    (r'^openid/$', 'begin', {'sreg': 'email'}),
    (r'^openid/complete/$', 'complete'),
    (r'^openid/signout/$', 'signout'),
)

urlpatterns += patterns('',
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'', include('ircious.ircious_app.urls')),
)
