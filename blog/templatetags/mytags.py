#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import template
import markdown

register = template.Library()


@register.filter
def mark(blog):
    blog.content = markdown.markdown(blog.content,
                                     extensions=[
                                         'markdown.extensions.extra',
                                         'markdown.extensions.codehilite',
                                         'markdown.extensions.toc',
                                     ])
    return blog.content
