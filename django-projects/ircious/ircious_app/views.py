from django.shortcuts import render_to_response, get_object_or_404
from ircious.ircious_app.models import LinkPost, LinkObj, User, IrcChannel, IrcNetwork, Nick
from ircious.ircious_app.forms import EditForm, RequestChannelForm
from ircious.ircious_app import utils
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import ObjectPaginator
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import Http404

def list(request, username=None, page=None, feed=False, channel=None, error=None):
    if page: 
        page=int(page)
    else:
        page=0
    p = LinkObj.objects.all()
    response_dict = _common(request)
    if error:
        response_dict['error']=error
    if username:
        p = p.filter(last_post__user__nick__nickname=username)
        try:
            response_dict['nick'] = Nick.objects.filter(nickname=username).get()
        except ObjectDoesNotExist:
            response_dict['error'] = "No such user"
    elif channel:
        p = p.filter(last_post__channel__name="#"+channel)
        response_dict['channel']=channel
    response_dict = _display_common(response_dict, page, p)
    response_dict['object_list'] = _post2link(response_dict)
    if not feed:
        return render_to_response('ircious_app/linkpost_list.html', response_dict)
    else:
        return render_to_response('ircious_app/linkpost_list_feed.html', response_dict, mimetype="application/atom+xml")

def showlink(request, slug=None, page=None, feed=False, url=None):
    if page: 
        page = int(page)
    else:
        page = 0
    obj = get_object_or_404(LinkObj, slug=slug)
    p = LinkPost.objects.filter(link__slug=slug)
    response_dict = _common(request)
    response_dict = _display_common(response_dict, page, p)
    response_dict['slug'] = slug
    response_dict['object'] = obj
    if not feed:
        return render_to_response('ircious_app/showlink.html', response_dict)
    else:
        return render_to_response('ircious_app/showlink_feed.html', response_dict, mimetype="application/atom+xml")

def favourites(request, username, page=None, feed=False):
    if page:
        page = int(page)
    else:
        page = 0
    users = User.objects.filter(nick__nickname=username)
    if not users:
        raise Http404
    else:
        user = users[0]
    p = user.favlinks.all()
    response_dict = _common(request)
    try:
        response_dict = _display_common(response_dict, page, p)
    except Http404:
        response_dict['error'] = "This user hasn't got any favourites"
    response_dict['object_list'] = _post2link(response_dict)
    response_dict['nick'] = username
    if not feed:
        return render_to_response('ircious_app/linkpost_list.html', response_dict)
    else:
        return render_to_response('ircious_app/linkpost_list_feed.html', response_dict, mimetype="application/atom+xml")

def search(request, searchstring, page, feed=False):
    if page:
        page = int(page)
    else:
        page = 0
    response_dict = _common(request)
    
    linkresults = LinkObj.objects.filter(title__search=searchstring)
    postresults = LinkPost.objects.filter(comment__search=searchstring)
    response_dict['object_list'] = postresults
    finalresults = _post2link(response_dict)
    finalresults.extend(linkresults)
    
    try:
        response_dict = _display_common(response_dict, page, finalresults)
    except Http404:
        response_dict['error'] = "No matches"
    response_dict['object_list'] = finalresults
    
    if not feed:
        return render_to_response('ircious_app/linkpost_list.html', response_dict)
    else:
        return render_to_response('ircious_app/linkpost_list_feed.html', response_dict, mimetype="application/atom+xml")

def _display_common(response_dict, page, p):
    paginator = ObjectPaginator(p, 20, 2)
    p = paginator.get_page(page)
    if not p:
        raise Http404
    response_dict['object_list'] = p
    response_dict['page'] = page
    
    if paginator.has_next_page(page):
        response_dict['next'] = page+1
    if paginator.has_previous_page(page):
        response_dict['prev'] = page-1
    return response_dict

def _post2link(response_dict):
    object_list = response_dict.get('object_list', [])
    def getPosts(x):
        try:
            res = x.linkpost_set.latest()
            user = response_dict.get('openid')
            if user and user in x.user_set.all():
                res.is_faved = True
            return res
        except ObjectDoesNotExist:
            return None
    object_list = map(getPosts, object_list)
    object_list = filter(lambda x: x, object_list)
    return object_list

def _common(request):
    popular = LinkObj().toplist(5)
    topusers = User().toplist(5)
    topchannels = IrcChannel().toplist(5)
    try:
        lastdate = LinkPost.objects.all()[0].date
    except IndexError:
        import datetime
        lastdate = datetime.datetime.now()
    response_dict = {'popular': popular, 'topusers': topusers, 'lastdate': lastdate, 'topchannels': topchannels}
    if request.openid:
        response_dict['openid'] = User.objects.filter(oid_url=request.openid)[0]
    return response_dict

def _post_validate(request, id, is_owner=True):
    response_dict = _common(request)
    if not request.openid:
        response_dict['error'] = "You naughty girl! You're not logged in!"
        return response_dict
    users = User.objects.filter(oid_url=request.openid)
    if users.count() != 1:
        response_dict['error'] = "Either you're not registered, or there are duplicates. Either way, this is bad"
        return response_dict
    user = users[0]
    objects = LinkPost.objects.filter(id=int(id))
    if objects.count() != 1:
        response_dict['error'] = "You're trying to muck with something that isn't here. Stop it!"
        return response_dict
    object = objects[0]
    if is_owner and object.user != user:
        response_dict['error'] = "You naughty boy! You're trying to play with other's content without consent!"
        return response_dict
    response_dict['object'] = object
    return response_dict

def delete_post(request, id):
    response_dict = _post_validate(request, id)
    if response_dict.has_key('error'):
        return render_to_response('ircious_app/linkpost_list.html', response_dict)
    object = response_dict.pop('object')
    linkobj = object.link
    object.delete()
    if linkobj.linkpost_set.count() == 0:
        linkobj.delete()
    return HttpResponseRedirect('/')

def edit_post(request, id):
    response_dict = _post_validate(request, id)
    if response_dict.has_key('error'):
        return render_to_response('ircious_app/linkpost_list.html', response_dict)
    object = response_dict['object']
    if request.method == 'POST':
        form = EditForm(request.POST)
        if form.is_valid():
            object.comment = form.cleaned_data['comment']
            if form.cleaned_data['recheck']:
                url = object.link.url
                try:
                    title = utils.getTitleFromUrl(url)
                except IOError:
                    return
                screenshot_url = utils.getYoutubeScreenshotUrl(url)
                object.link.title=title
                object.link.slug=utils.slugify(title)
                object.link.screenshot=screenshot_url
                object.link.save()
            object.save()
            return HttpResponseRedirect(reverse('ircious.ircious_app.views.showlink', kwargs={'slug': object.link.slug}))
    else:
        form = EditForm({'comment': object.comment})
    response_dict['form'] = form
    return render_to_response('ircious_app/edit.html', response_dict)

def add_channel(request):
    response_dict = _common(request)
    if request.method == 'POST':
        form = RequestChannelForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            network = IrcNetwork.objects.filter(name=data['network'])
            if not network:
                network = IrcNetwork(name=data['network'])
                network.save()
            else:
                network = network[0]
            if not IrcChannel.objects.filter(name=data['channel'], network=network):
                ic = IrcChannel(name=data['channel'], network=network, requested_by=data['nick'])
                ic.save()
            return HttpResponseRedirect('/')
    else:
        form = RequestChannelForm()
    response_dict['form'] = form
    return render_to_response('ircious_app/add_channel.html', response_dict)

def add_favlist(request, id):
    response_dict = _post_validate(request, id, False)
    if response_dict.has_key('error'):
        return render_to_response('ircious_app/favourite.html', response_dict)
    linkobj = response_dict.pop('object').link
    if (response_dict['openid'].favlinks.filter(id=linkobj.id)):
        response_dict['openid'].favlinks.remove(linkobj)
    else:
        response_dict['openid'].favlinks.add(linkobj)
    response_dict['openid'].save()
    return render_to_response('ircious_app/favourite.html', response_dict)
