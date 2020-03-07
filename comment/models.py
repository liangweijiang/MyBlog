"""
评论功能
"""

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
import threading


# Create your models here.
class Comment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    # 评论内容
    text = models.TextField()
    # 评论时间
    comment_time = models.DateTimeField(auto_now_add=True)
    # 评论人
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # 回复的评论
    parent = models.ForeignKey('self', null=True, related_name='parent_comment', on_delete=models.CASCADE)
    # 这个字段保存评论的上最上一层
    root = models.ForeignKey('self', related_name='root_comment', null=True, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-comment_time']

    def send_email(self):
        if self.parent is None:
            subject = '有人评论你的博客'
            email = self.content_object.get_email()
        else:
            subject = '有人回复你的评论'
            email = self.parent.content_object.get_email()
        if email != '':
            context = {}
            context['comment_text'] = self.text
            context['url'] = self.content_object.get_url()
            print('--------->', self.text, self.content_object.get_url())
            text = render(None, 'send_email.html', context).content.decode('utf-8')
            send_mail = SendEmail(subject, text, email)
            send_mail.start()
            return True
        else:
            return False


class SendEmail(threading.Thread):
    def __init__(self, subject, text, email, fail_silently=False):
        super().__init__()
        self.subject = subject
        self.text = text
        self.email = email
        self.fail_silently = fail_silently

    def run(self):
        send_mail(
            self.subject,
            '',
            settings.EMAIL_HOST_USER,
            [self.email],
            fail_silently=self.fail_silently,
            html_message=self.text
        )
