#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.urls import path
from . import views

# start with blog
urlpatterns = [
    # http://localhost:8000/blog/1
    path('', views.like_change, name="like_change"),

]
