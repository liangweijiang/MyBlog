#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .views import login, register, v_code, logout, send_verification_code, personal_info, bind_email,change_password,find_password
from django.urls import path

urlpatterns = [
    path('v_code/', v_code, name='v_code'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('register/', register, name='register'),
    path('send_verification_code/', send_verification_code, name='send_verification_code'),
    path('personal_info/', personal_info, name='personal_info'),
    path('bind_email/', bind_email, name='bind_email'),
    path('change_password/', change_password, name='change_password'),
    path('find_password/', find_password, name='find_password'),
]
