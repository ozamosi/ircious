from django.db import models, connection

# Create your models here.
class LinkObj(models.Model):
    url = models.URLField()
    title = models.CharField(max_length=200)
    slug = models.SlugField(prepopulate_from=("title",))
    last_post = models.ForeignKey('LinkPost', blank=True, null=True)
    class Admin:
        pass
    def __unicode__(self): return self.title
    def toplist(self, numobjects):
        fieldlist = ['url', 'title', 'slug']
        long_fieldlist = map((lambda x: 'ircious_app_linkobj.'+x), fieldlist)
        cursor = connection.cursor()
        cursor.execute("SELECT "+ ", ".join(long_fieldlist) + ", COUNT(ircious_app_linkpost.link_id) AS num FROM ircious_app_linkobj INNER JOIN ircious_app_linkpost ON ircious_app_linkobj.id = ircious_app_linkpost.link_id GROUP BY ircious_app_linkobj.id ORDER BY num DESC LIMIT %i" % numobjects)
        result = cursor.fetchall()
        fieldlist += ['num']
        return map((lambda x: dict(zip(fieldlist, x))), result)
    class Meta:
        ordering = ['-last_post_id']
        get_latest_by = "last_post_id"
                    

class User(models.Model):
    oid_url = models.URLField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    class Admin:
        pass
    def toplist(self, numobjects):
        cursor = connection.cursor()
        cursor.execute("SELECT ircious_app_nick.nickname, COUNT(ircious_app_linkpost.user_id) AS num FROM ircious_app_user INNER JOIN ircious_app_nick ON ircious_app_nick.user_id = ircious_app_user.id INNER JOIN ircious_app_linkpost ON ircious_app_user.id = ircious_app_linkpost.user_id GROUP BY ircious_app_user.id ORDER BY num DESC LIMIT %i" % numobjects)
        result = cursor.fetchall()
        fieldlist = ['nick', 'num']
        return map((lambda x: dict(zip(fieldlist, x))), result)
    def __unicode__(self):
        return (self.oid_url) or ("User %i" % self.id)

class IrcNetwork(models.Model):
    name = models.CharField(max_length=30)
    uri = models.CharField(max_length=200)
    bot_nick = models.CharField(max_length=30)
    def __unicode__(self): return self.name
    class Admin:
        pass

class IrcChannel(models.Model):
    name = models.CharField(max_length=30, core=True)
    network = models.ForeignKey(IrcNetwork, edit_inline=models.STACKED, num_in_admin=3)
    def __unicode__(self): return self.name
    class Admin:
        pass
    def toplist(self, numobjects):
        cursor = connection.cursor()
        cursor.execute("SELECT ircious_app_ircchannel.name, ircious_app_ircnetwork.uri, COUNT(ircious_app_linkpost.channel_id) AS num FROM ircious_app_ircchannel INNER JOIN ircious_app_ircnetwork ON ircious_app_ircchannel.network_id = ircious_app_ircnetwork.id LEFT JOIN ircious_app_linkpost ON ircious_app_ircchannel.id = ircious_app_linkpost.channel_id GROUP BY ircious_app_ircchannel.id ORDER BY num DESC LIMIT %i" % numobjects)
        result = cursor.fetchall()
        fieldlist = ['name', 'network_uri','num']
        return map((lambda x: dict(zip(fieldlist, x))), result)


class LinkPost(models.Model):
    link = models.ForeignKey(LinkObj)
    user = models.ForeignKey(User)
    comment = models.CharField(max_length=200, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    channel = models.ForeignKey(IrcChannel)
    class Admin:
        pass
    class Meta:
        ordering = ['-date']
        get_latest_by = "date"
    def __unicode__(self): return self.comment

class Nick(models.Model):
    nickname = models.CharField(max_length=30, core=True)
    user = models.ForeignKey(User, edit_inline=models.STACKED, num_in_admin=1)
    verified_user = models.BooleanField(default=False)
    class Admin:
        pass
