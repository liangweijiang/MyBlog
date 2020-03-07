from django.shortcuts import render, redirect, reverse
from django.views import View
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from PIL import Image, ImageDraw, ImageFont
from django.http import HttpResponse
import random
from user.forms import LoginForm, RegForm, BindEmailForm, ChangePasswordForm, FindPasswordForm
import string
import time
from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib.auth.models import User


def v_code(request):
    """
    处理验证码的函数
    :param request:
    :return:
    """
    img_obj = Image.new('RGB', (200, 43), random_color())
    # 生成画布
    draw_obj = ImageDraw.Draw(img_obj)
    # 字体的样式
    font_obj = ImageFont.truetype('static/font/kumo.ttf', 28)
    code_temp = []
    for i in range(4):
        lower = chr(random.randint(97, 122))
        upper = chr(random.randint(65, 90))
        number = str(random.randint(0, 9))
        choice = random.choice([lower, upper, number])
        code_temp.append(choice)
        draw_obj.text((i * 40 + 35, 0), choice, fill=random_color(), font=font_obj)

    # 加干扰线
    width = 390  # 图片宽度（防止越界）
    height = 35
    for i in range(5):
        x1 = random.randint(0, width)
        x2 = random.randint(0, width)
        y1 = random.randint(0, height)
        y2 = random.randint(0, height)
        draw_obj.line((x1, y1, x2, y2), fill=random_color())

    # 存入session, 方便验证
    request.session['v_code'] = ''.join(code_temp).upper()
    # 将图片加载进内存
    from io import BytesIO
    f1 = BytesIO()
    img_obj.save(f1, format="PNG")
    img_data = f1.getvalue()

    return HttpResponse(img_data, content_type='image/png')


def random_color():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def login(request):
    if request.method == 'POST':
        v_code = request.POST.get('v_code').upper()
        if v_code == request.session['v_code']:
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                user = login_form.cleaned_data.get('user')
                auth.login(request, user)
                return redirect(request.GET.get('next', reverse('index')))
        else:
            context = {}
            err_msg = '验证码错误'
            login_form = LoginForm()
            context['login_form'] = login_form
            context['err_msg'] = err_msg
            return render(request, 'login.html', context)
    else:
        login_form = LoginForm()
    context = {}
    context['login_form'] = login_form
    return render(request, 'login.html', context)


def register(request):
    if request.method == 'POST':
        email_code = request.POST.get('email_code').upper()
        reg_form = RegForm(request.POST)
        if email_code == request.session.get('bind_email_code', '').upper():
            if reg_form.is_valid():
                # 创建新用户
                # 方法一
                # form_obj.cleaned_data.pop('re_password')
                # models.UserProfile.objects.create_user(**form_obj.cleaned_data)
                # 方法二
                obj = reg_form.save()
                obj.set_password(obj.password)
                obj.save()
                del request.session['bind_email_code']
                return redirect(request.GET.get('next', reverse('login')))
        else:
            context = {}
            context['reg_form'] = reg_form
            context['error'] = '验证码错误'
            return render(request, 'register.html', context)
    else:
        reg_form = RegForm()
    context = {}
    context['reg_form'] = reg_form
    return render(request, 'register.html', context)


def personal_info(request):
    context = {}
    bind_form = BindEmailForm()
    password_form = ChangePasswordForm()
    context['bind_form'] = bind_form
    context['password_form'] = password_form
    return render(request, 'presonal_info.html', context)


def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('next', reverse('index')))


def send_verification_code(request):
    email = request.GET.get('email')
    send_for = request.GET.get('send_for')
    data = {}
    if email:
        v_code = ''.join(random.sample(string.ascii_letters + string.digits, 4))
        now = int(time.time())
        send_code_time = request.session.get('send_code_time', 0)
        if now - send_code_time < 30:
            data['status'] = 'ERROR'
        else:
            request.session[send_for] = v_code
            request.session['get_email'] = email
            request.session['send_code_time'] = now

            # 发送邮件
            send_mail(
                '绑定邮箱',
                '验证码：%s' % v_code,
                '1210457866@qq.com',
                [email],
                fail_silently=False,
            )
            data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)


def bind_email(request):
    data = {}
    bind_form = BindEmailForm(request.POST, request=request)
    if bind_form.is_valid():
        email = bind_form.cleaned_data['email']
        request.user.email = email
        request.user.save()
        del request.session['bind_email_code']
        del request.session['get_email']
        data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
        data['errors'] = bind_form.errors
    return JsonResponse(data)


def change_password(request):
    data = {}
    password_form = ChangePasswordForm(request.POST, user=request.user)
    if password_form.is_valid():
        user = request.user
        new_password = password_form.cleaned_data['new_password']
        user.set_password(new_password)
        user.save()
        auth.logout(request)
        data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
        data['errors'] = password_form.errors
    return JsonResponse(data)


def find_password(request):
    if request.method == 'POST':
        find_form = FindPasswordForm(request.POST, request=request)
        if find_form.is_valid():
            email = find_form.cleaned_data['email']
            new_password = find_form.cleaned_data['new_password']
            user = User.objects.filter(email=email).first()
            user.set_password(new_password)
            user.save()
            # 清除session
            del request.session['find_password_code']
            del request.session['get_email']
            return redirect(request.GET.get('next', reverse('login')))
    else:
        find_form = FindPasswordForm()
    context = {}
    context['find_form'] = find_form
    return render(request, 'find_password.html', context)


# 用来验证是否已经登录
class LoginRequired(View):
    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super().as_view(*args, **kwargs)
        return login_required(view)
