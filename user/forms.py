#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from django.forms import widgets
from django.contrib import auth
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class BaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for filed in self.fields.values():
            filed.widget.attrs.update({'class': 'input-material'})


class LoginForm(forms.ModelForm):
    username = forms.CharField(label='用户名',
                               widget=forms.TextInput(
                                   attrs={'placeholder': '请输入用户名', 'id': 'username', 'class': 'input-material'}),
                               error_messages={'required': '请输入用户名'}
                               )
    password = forms.CharField(label='密码',
                               widget=forms.PasswordInput(
                                   attrs={'placeholder': '请输入密码', 'id': 'password', 'class': 'input-material'}),
                               error_messages={'required': '请输入密码'}
                               )

    class Meta:
        model = User
        fields = ['username', 'password']
        labels = {
            'username': '用户名',
            'password': '密码'
        }

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is None:
            raise ValidationError('Wrong user name or password')
        else:
            self.cleaned_data['user'] = user
        return self.cleaned_data


class RegForm(BaseForm):
    password = forms.CharField(
        label='密码',
        min_length=8,
        max_length=16,
        widget=widgets.PasswordInput(attrs={'id': 'register-password', 'placeholder': '请输入密码'}),
    )
    re_password = forms.CharField(
        label='确认密码',
        widget=forms.widgets.PasswordInput(attrs={'id': 'register-passwords', 'placeholder': '确认密码'})
    )

    class Meta:
        model = User
        # fields = '__all__'   # 所有字段
        fields = ['username', 'password', 're_password', 'email']  # 指定字段
        # exclude = ['']
        widgets = {
            'username': forms.widgets.TextInput(attrs={'id': 'register-username', 'placeholder': '请输入用户名'}),
            'email': forms.widgets.EmailInput(attrs={'id': 'register-email', 'placeholder': '请输入邮箱'}),
        }

        labels = {
            'username': '用户名',
            'password': '密码',
            'name': '姓名',
            'email': '邮箱'
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already exists')
        return email

    def clean_password_again(self):
        password = self.cleaned_data['password']
        password_again = self.cleaned_data['re_password']
        if password != password_again:
            raise forms.ValidationError('Inconsistent passwords twice')
        return password_again


class BindEmailForm(forms.Form):
    email = forms.EmailField(
        label='邮箱',
        widget=forms.EmailInput(
            attrs={'class': 'form-control mode-control', 'placeholder': '请输入正确的邮箱'}
        )
    )
    verification_code = forms.CharField(
        label='验证码',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control mode-control', 'placeholder': '点击“发送验证码”发送到邮箱'}
        )
    )

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(BindEmailForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 判断用户是否登录
        if self.request.user.is_authenticated:
            self.cleaned_data['user'] = self.request.user
        else:
            raise forms.ValidationError('用户尚未登录')

        # # 判断用户是否已绑定邮箱
        # if self.request.user.email != '':
        #     raise forms.ValidationError('你已经绑定邮箱')

        # 判断验证码
        code = self.request.session.get('bind_email_code', '').upper()
        verification_code = self.cleaned_data.get('verification_code', '').upper()
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码不正确')
        return self.cleaned_data

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已经被绑定')
        # 判断邮箱是否是发送验证码的邮箱
        get_email = self.request.session.get('get_email', '')
        if get_email != email:
            raise forms.ValidationError('输入的邮箱与发送验证码的邮箱不符')
        return email

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')
        return verification_code


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        label='旧密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control mode-control', 'placeholder': '请输入旧的密码'})
    )

    new_password = forms.CharField(
        label='新密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control mode-control', 'placeholder': '请输入新的密码'})
    )

    re_password = forms.CharField(
        label='重复新密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control mode-control', 'placeholder': '请再次输入密码'})
    )

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean(self):
        # 验证新的密码是否一致
        new_password = self.cleaned_data.get('new_password', '')
        re_password = self.cleaned_data.get('re_password', '')
        if new_password != re_password or new_password == '':
            raise forms.ValidationError('两次输入的密码不一致')
        return self.cleaned_data

    def clean_old_password(self):
        # 校验旧密码是否正确
        old_password = self.cleaned_data.get('old_password', '')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('旧密码错误')
        return old_password


class FindPasswordForm(forms.Form):
    email = forms.EmailField(
        label='邮箱',
        widget=forms.EmailInput(
            attrs={'class': 'input-material mode-control', 'placeholder': '请输入正确的邮箱'}
        )
    )
    verification_code = forms.CharField(
        label='验证码',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'input-material mode-control', 'placeholder': '点击“发送验证码”发送到邮箱'}
        )
    )
    new_password = forms.CharField(
        label='新的密码',
        widget=forms.PasswordInput(
            attrs={'class': 'input-material mode-control', 'placeholder': '请输入新的密码'}
        )
    )

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(FindPasswordForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('邮箱不存在')
        get_email = self.request.session.get('get_email', '')
        if get_email != email:
            raise forms.ValidationError('输入的邮箱与发送验证码的邮箱不符')
        return email

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')

        # 判断验证码
        code = self.request.session.get('find_password_code', '').upper()
        verification_code = self.cleaned_data.get('verification_code', '').upper()
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码不正确')

        return verification_code


