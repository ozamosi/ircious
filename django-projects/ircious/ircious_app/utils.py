# -*- encoding: utf-8 -*-
from ircious.ircious_app.models import LinkObj, User, LinkPost, Nick, IrcNetwork, IrcChannel
from urllib2 import urlopen
from htmlentitydefs import name2codepoint
import re

try:
    import xml.etree.ElementTree as ET
except ImportError:
    try:
        import CElementTree as ET
    except ImportError:
        try:
            import elementtree.ElementTree as ET
        except ImportError:
            import lxml.etree as ET
# ...because there's only one way to do things in Python

# Try to support both OpenID 1.2 and 2.0:
try:
    from openid import oidutil
    normalizeUrl = oidutil.normalizeUrl
except AttributeError:
    from openid import urinorm
    normalizeUrl = urinorm.urinorm

entityregex = re.compile('&[a-zA-Z0-9#]+;')

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
    >>> u = User()
    >>> u.save()
    >>> inw = IrcNetwork()
    >>> inw.save()
    >>> ic = IrcChannel(name="ircious", network=inw, requested_by=u)
    >>> ic.save()
    >>> addPost('test-nick', 'ircious', 'http://example.com', 'Super-cool')
    >>> lo = LinkObj.objects.filter(last_post__comment='Super-cool')[0]
    >>> lo.screenshot
    >>> addPost('test-nick2', 'ircious', 'http://youtube.com/watch?v=_y36fG2Oba0', 'Great!')
    >>> lo = LinkObj.objects.filter(last_post__comment='Great!')[0]
    >>> lo.screenshot
    u'http://img.youtube.com/vi/_y36fG2Oba0/default.jpg'
    >>> addPost('test-nick3', 'ircious', 'http://example.com', 'Amazing')
    >>> lo = LinkObj.objects.all()[0]
    >>> lo.last_post.comment
    u'Amazing'
    """
    correctuser = getUserWithNick(nick)
    channelobjs = IrcChannel.objects.filter(name=channel)
    if not channelobjs:
        raise ValueError, "Invalid channel"
    channelobj = channelobjs[0]
    existinglinkobj = LinkObj.objects.filter(url=url)
    if not existinglinkobj:
        try:
            title = getTitleFromUrl(url)
        except IOError:
            return
        if 'youtube' in url:
            screenshot_url = getYoutubeScreenshotUrl(url)
        elif 'flickr' in url:
            screenshot_url = getFlickrScreenshotUrl(url)
        else:
            screenshot_url = ""
        slug = slugify(title)
        if LinkObj.objects.filter(slug=slug):
            num = 1
            while LinkObj.objects.filter(slug=slug+str(num)):
                num += 1
            slug = slug + str(num)
        correctlinkobj = LinkObj(url=url, title=title, slug=slug, screenshot=screenshot_url)
        correctlinkobj.save()
    else:
        correctlinkobj = existinglinkobj[0]
    
    lp = LinkPost(link=correctlinkobj, user=correctuser, comment=descr, channel=channelobj)
    lp.save()
    correctlinkobj.last_post = lp
    correctlinkobj.save()

def getTitleFromUrl(url):
    """
    Download the URL and try to extract a title
    
    >>> #Has proper title
    >>> getTitleFromUrl('http://google.com')
    'Google'
    >>> #Fallback to <h1>
    >>> getTitleFromUrl('http://flukkost.nu') == 'Flukkosten är serverad!'
    True
    >>> #Fallback to first line
    >>> getTitleFromUrl('http://www.0xdeadbeef.com/html/monkeys.txt')
    'I LIKE MONKEYS'
    >>> getTitleFromUrl('http://use.perl.org/images/pix.gif')
    'http://use.perl.org/images/pix.gif'
    >>> #XML Entities
    >>> getTitleFromUrl('http://brad.livejournal.com/2345245.html')
    "brad's life - My Halloween Costume...."
    >>> #HTML Entities
    >>> getTitleFromUrl('http://www.blinkenlights.se/user/ozamosi') == 'Blinkenlights.se - Användarprofil - Programmering & spelutveckling'
    True
    """
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
                    try:
                        title = pagecontents[:pagecontents.index('\n')]
                    except ValueError:
                        title = url
                else:
                    title = url
    # Try to autodetect the encoding
    try:
        title = title.decode('utf-8')
    except UnicodeDecodeError:
        title = title.decode('latin-1')
    # Remove all entities
    matches = entityregex.finditer(title)
    replacedict = {}
    for match in matches:
        entity = title[match.start():match.end()]
        try:
            replacedict[entity] = unichr(name2codepoint[entity[1:-1]])
        except KeyError:
            try: # &#nnnn; base10
                replacedict[entity] = unichr(int(entity[2:-1]))
            except ValueError: # &#xhhhh; base16
                replacedict[entity] = unichr(int(entity[3:-1], 16))
    for entity in replacedict:
        title = title.replace(entity, replacedict[entity])
    return title.strip().encode('utf-8')

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
    if "bot" in nick.lower():
        raise ValueError, "Bot's aren't allowed to post links"
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

def getFlickrScreenshotUrl(url):
    """
    From a Flickr URL, retrieve a screenshot

    >>> getFlickrScreenshotUrl('http://www.flickr.com/photos/psd/1805709102/')
    'http://farm3.static.flickr.com/2189/1805709102_4fc795431b_t.jpg'
    >>> getFlickrScreenshotUrl('http://www.flickr.com/photo_zoom.gne?id=1805709102&size=l')
    'http://farm3.static.flickr.com/2189/1805709102_4fc795431b_t.jpg'
    >>> getFlickrScreenshotUrl('')
    """
    if not url.startswith('http://flickr.com') and not url.startswith('http://www.flickr.com'):
        return None
    id = url.strip('/').split('/')[-1]
    try:
        int(id)
    except ValueError:
        try:
            start = url.index('id=')+3
        except ValueError:
            return None
        try:
            end = url.index('&', start)
        except ValueError:
            end = len(url)
        id = url[start:end]
    response = urlopen("http://api.flickr.com/services/rest/?method=flickr.photos.getSizes&api_key=a6ccec61d8016d9b4bac0ccea3139654&photo_id="+id)
    tree = ET.parse(response)
    for node in tree.findall('sizes/size'):
        if node.attrib['label'] == 'Thumbnail':
            return node.attrib['source']

def slugify(inStr):
    removelist = ["a", "an", "as", "at", "before", "but", "by", "for","from","is", "in", "into", "like", "of", "off", "on", "onto","per","since", "than", "the", "this", "that", "to", "up", "via","with"];
    for a in removelist:
        aslug = re.sub(r'\b'+a+r'\b','',inStr)
        aslug = re.sub('[^\w\s-]', '', aslug).strip().lower()
        aslug = re.sub('\s+', '-', aslug)
        aslug = aslug[0:50]
        return aslug
