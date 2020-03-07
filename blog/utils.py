#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db.models import Sum
from .models import Blog


def get_hot_blogs():
    hot_blogs = Blog.objects.all().order_by('-read_nums__read_num')
    return hot_blogs[:7]
