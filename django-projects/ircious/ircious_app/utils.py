from ircious.ircious_app.models import LinkObj, User, LinkPost, Nick, IrcNetwork, IrcChannel
from urllib2 import urlopen
from htmlentitydefs import name2codepoint
import re
# Try to support both OpenID 1.2 and 2.0:
try:
    from openid import oidutil
    normalizeUrl = oidutil.normalizeUrl
except AttributeError:
    from openid import urinorm
    normalizeUrl = urinorm.urinorm
            

def addOidUser(nick, url, fromirc=True):
    """
    Add OpenID to users profile, making sure the URL is syntactically correct
    
    >>> addOidUser('test-nick', 'http://example.com')
    >>> addOidUser('test-nick', 'example.com')
    Traceback (most recent call last):
    ...
    ValueError: No scheme specified
    >>> addOidUser('test-nick2', 'http://example.com', False)
    >>> u1 = Nick.objects.filter(nickname='test-nick')[0]
    >>> u2 = Nick.objects.filter(nickname='test-nick2')[0]
    >>> u1.verified_user
    True
    >>> u2.verified_user
    False
    """
    
    correctuser = getUserWithNick(nick)
    nick = correctuser.nick_set.filter(nickname=nick)[0]
    if fromirc and nick:
        nick.verified_user = fromirc
        nick.save()
    oid_url = normalizeUrl(url)
    if not oid_url:
        raise ValueError
    correctuser.oid_url = oid_url
    correctuser.save()

def addPost(nick, channel, url, descr):
    """
    Add post to database

    >>> addPost('test-nick', 'test-channel', 'http://example.com', 'Super-cool')
    Traceback (most recent call last):
    ...
    ValueError: Invalid channel
    >>> b = IrcNetwork()
    >>> b.save()
    >>> a = IrcChannel(name="ircious", network=b)
    >>> a.save()
    >>> addPost('test-nick', 'ircious', 'http://example.com', 'Super-cool')
    >>> p = LinkObj.objects.filter(last_post__comment='Super-cool')[0]
    >>> p.screenshot
    >>> addPost('test-nick2', 'ircious', 'http://youtube.com/watch?v=_y36fG2Oba0', 'Great!')
    >>> p = LinkObj.objects.filter(last_post__comment='Great!')[0]
    >>> p.screenshot
    u'http://img.youtube.com/vi/_y36fG2Oba0/default.jpg'
    >>> addPost('test-nick3', 'ircious', 'http://example.com', 'Amazing')
    >>> p = LinkObj.objects.all()[0]
    >>> p.last_post.comment
    u'Amazing'
    """
    channelobjs = IrcChannel.objects.filter(name=channel)
    if not channelobjs:
        raise ValueError, "Invalid channel"
    channelobj = channelobjs[0]
    existinglinkobj = LinkObj.objects.filter(url=url)
    if not existinglinkobj:
        try:
            page = urlopen(url)
            if page.headers.maintype not in ['text', 'application']: #If it's not text, html or XML, basicly
                title = url
            else:
                pagecontents =  page.read()
                try:
                    start = pagecontents.lower().index("<title>") + len("<title>")
                    end = pagecontents.lower().index("</title>", start)
                    title = pagecontents[start:end]
                except ValueError:
                    try:
                        start = pagecontents.lower().index("<h1>") + len("<h1>")
                        end = pagecontents.lower().index("</h1>", start)
                        title = pagecontents[start:end]
                    except ValueError:
                        if page.headers.type in ['text/plain']:
                            title = page[:50]+"..."
                        else:
                            title = url
            screenshot_url = getYoutubeScreenshotUrl(url)
            try:
                title = title.decode('utf-8')
            except UnicodeDecodeError:
                title = title.decode('latin-1')
            for x in name2codepoint:
                title = title.replace('&'+x+';', unichr(name2codepoint[x]))
            title.encode('utf-8')
        except IOError:
            return
        correctlinkobj = LinkObj(url=url, title=title, slug=_slugify(title), screenshot=screenshot_url)
        correctlinkobj.save()
    else:
        correctlinkobj = existinglinkobj[0]
    correctuser = getUserWithNick(nick)
    
    lp = LinkPost(link=correctlinkobj, user=correctuser, comment=descr, channel=channelobj)
    lp.save()
    correctlinkobj.last_post = lp
    correctlinkobj.save()

def getUserWithNick(nick):
    """
    Get a user object from a specified nickname

    >>> a = getUserWithNick("test")
    >>> b = getUserWithNick("test2")
    >>> c = getUserWithNick("test")
    >>> a == b
    False
    >>> a == c
    True
    """
    existinguser = User.objects.filter(nick__nickname=nick)
    if not existinguser:
        correctuser = User()
        correctuser.save()
        n = Nick(nickname=nick, user=correctuser)
        n.save()
    else:
        if len(existinguser) > 1:
            raise ValueError, "Multiple users with this nick :S"
        correctuser = existinguser[0]
    return correctuser

def getYoutubeScreenshotUrl(url):
    """
    From a Youtube URL, retrieve the screenshot

    >>> getYoutubeScreenshotUrl('http://youtube.com/watch?v=_y36fG2Oba0')
    'http://img.youtube.com/vi/_y36fG2Oba0/default.jpg'
    >>> getYoutubeScreenshotUrl('')
    """
    if not url.startswith("http://youtube.com") and not url.startswith("http://www.youtube.com"):
        return None
    try:
        start = url.index('v=')+2
    except ValueError:
        return None
    try:
        end = url.index('&', start)
    except ValueError:
        end = len(url)
    videoid = url[start:end]
    response = urlopen("http://www.youtube.com/api2_rest?method=youtube.videos.get_details&dev_id=6PcFFFsNxi4&video_id=%s" % videoid)
    xmlfile = response.read()
    start = xmlfile.index("<thumbnail_url>") + len("<thumbnail_url>")
    end = xmlfile.index("</thumbnail_url>")
    return xmlfile[start:end]

def _slugify(inStr):
    removelist = ["a", "an", "as", "at", "before", "but", "by", "for","from","is", "in", "into", "like", "of", "off", "on", "onto","per","since", "than", "the", "this", "that", "to", "up", "via","with"];
    for a in removelist:
        aslug = re.sub(r'\b'+a+r'\b','',inStr)
        aslug = re.sub('[^\w\s-]', '', aslug).strip().lower()
        aslug = re.sub('\s+', '-', aslug)
        aslug = aslug[0:50]
        return aslug
