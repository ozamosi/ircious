#!/usr/bin/python2.4
from django import template
from django.template.defaultfilters import stringfilter
import md5 as md5lib
register = template.Library()

@register.filter
@stringfilter
def strip(string, stripchars):
    "Removes all stripchars from begining and end of string"
    return string.strip(stripchars)

@register.filter
@stringfilter
def md5(string):
    "Returns MD5 checksum for string. Usefull for gravatars"
    return md5lib.new(string).hexdigest()
