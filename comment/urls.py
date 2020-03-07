#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.urls import path
from . import views

urlpatterns = [
    path('', views.update_comment, name="update_comment"),
    # path('ck/', views.reply_ckeditor, name="reply_ckeditor"),
]
