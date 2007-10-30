#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad, ip_quad_to_numstr
import irclib
import sys, traceback
sys.path += ['/home/ozamosi/ircious/django_src']
sys.path += ['/home/ozamosi/ircious/django-projects']
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'ircious.settings'
from ircious.ircious_app import utils
from ircious.ircious_app.models import IrcNetwork

class TestBot(SingleServerIRCBot):
    def __init__(self, channels, nickname, server, port=6667):
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.my_channels = channels

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        for channel in self.my_channels:
            c.join(channel)

    def on_pubmsg(self, c, e):
        comment = e.arguments()[0]
        nick = nm_to_n(e.source())
        if irc_lower(comment).startswith(irc_lower(self.connection.get_nickname()+": openid=")):
            try:
                utils.addOidUser(nick, comment[len(self.connection.get_nickname()+": openid="):])
                self.connection.privmsg(e.target(), "Ok")
            except ValueError, LookupError:
                self.connection.privmsg(e.target(), "Invalid OpenID")
        elif "http://" in comment:
            start = comment.find("http://")
            end = comment.find(" ", start)
            
            if end != -1:
                url = comment[start:end]
            else:
                url = comment[start:]
            url.rstrip('/')

            if start and end != -1:
                descr = comment
            elif start:
                descr = comment[:start]
            elif end != -1:
                descr = comment[end:]
            else:
                descr = ""
            descr = descr.strip().rstrip(":")
            try:
                descr.decode('utf-8')
            except UnicodeDecodeError:
                descr = descr.decode('latin-1').encode('utf-8')
            try:
                utils.addPost(nick, e.target(), url, descr)
            except:
                traceback.print_exc(file=sys.stdout)
        elif comment == "disconnect" and nick == "ozamosi":
            self.disconnect()
            sys.exit()

def main():
    if "--debug" in sys.argv:
        print "Debugging..."
        irclib.DEBUG=1
    if "--only-ircious" in sys.argv:
        bot = TestBot(['#ircious'], 'ircious', 'irc.freenode.net', 6667)
        bot.start()
        return
    for network in IrcNetwork.objects.all():
        bot = TestBot(network.ircchannel_set.all(), network.bot_nick, network.uri, 6667)
        bot.start()

if __name__ == "__main__":
    main()