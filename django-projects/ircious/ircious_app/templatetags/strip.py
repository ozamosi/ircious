#!/usr/bin/python2.4
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def strip(string, stripchars):
    "Removes all stripchars from begining and end of string"
    return string.strip(stripchars)
