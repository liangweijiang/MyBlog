#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.urls import path
from . import views

# start with blog
urlpatterns = [
    # http://localhost:8000/blog/1
    path('<int:blog_pk>', views.BlogDetail.as_view(), name="blog_detail"),
    path('', views.BlogList.as_view(), name="index"),
    path('type/', views.BlogTypeView.as_view(), name="blogs_with_type"),
    path('date/', views.BlogDateView.as_view(), name="blogs_with_date"),
]
