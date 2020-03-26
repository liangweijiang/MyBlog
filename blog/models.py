from django.db import models
from django.contrib.auth.models import User
from read_statistics.models import ReadNumExpandMethod, ReadNum
from django.contrib.contenttypes.fields import GenericRelation
from django.shortcuts import reverse


# Create your models here.

class BlogType(models.Model):
    """
    博客的类型, 一篇博文只有一个分类
    """
    type_name = models.CharField(max_length=15)

    def __str__(self):
        return self.type_name


class Blog(models.Model, ReadNumExpandMethod):
    """
    包括标题,类型, 内容,作者, 发表时间,更新时间
    """
    title = models.CharField(max_length=48)
    blog_type = models.ForeignKey(to='BlogType', blank=True, null=True, on_delete=models.CASCADE)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    last_updated_time = models.DateTimeField(auto_now_add=True)
    read_nums = GenericRelation(ReadNum)
    sticky = models.IntegerField(default=0)

    def __str__(self):
        return '<{}>'.format(self.title)

    class Meta:
        ordering = ['-sticky', '-last_updated_time', '-created_time']

    def get_url(self):
        return reverse('blog_detail', kwargs={'blog_pk': self.pk})

    def get_email(self):
        return self.author.email
