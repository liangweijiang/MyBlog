from django.shortcuts import render, get_object_or_404
from .models import Blog, BlogType
from django.views import View
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Count
import markdown
from read_statistics.utils import read_statistics_once_read
from .utils import get_hot_blogs
from django.core.cache import cache

# Create your views here.
def get_blog_list_attribute(request, blogs_all_list):
    context = {}
    paginator = Paginator(blogs_all_list, settings.EACH_PAGE_BLOGS_NUMBER)
    page_num = request.GET.get('page', 1)
    page_of_blogs = paginator.get_page(page_num)
    # 获取博客所有的日期
    blog_dates = Blog.objects.dates('created_time', 'month', order="DESC")
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_for_date = Blog.objects.filter(created_time__year=blog_date.year,
                                            created_time__month=blog_date.month)
        blog_dates_dict[blog_date] = [blog_for_date, blog_for_date.count()]
    context['blogs'] = page_of_blogs.object_list
    context['page_of_blogs'] = page_of_blogs
    context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog'))
    context['blog_dates'] = blog_dates_dict
    return context


class BlogList(View):
    def get(self, request, blog_pk=None):
        blog_all_list = Blog.objects.all()
        context = get_blog_list_attribute(request, blog_all_list)
        hot_blogs = cache.get('hot_blogs')
        if not hot_blogs:
            hot_blogs = get_hot_blogs()
            cache.set('hot_blogs', hot_blogs, 3600)
        context['hot_blogs'] = hot_blogs
        return render(request, 'index.html', context)


class BlogDetail(View):
    def get(self, request, blog_pk):
        context = {}
        blog = get_object_or_404(Blog, pk=blog_pk)
        blog.content = markdown.markdown(blog.content,
                                         extensions=[
                                             'markdown.extensions.extra',
                                             'markdown.extensions.codehilite',
                                             'markdown.extensions.toc',
                                         ])
        context['blog'] = blog
        context['previous_blog'] = Blog.objects.filter(id__lt=blog_pk).first()
        context['next_blog'] = Blog.objects.filter(id__gt=blog_pk).last()
        response = render(request, 'blog_detail.html', context)
        key = read_statistics_once_read(request, blog)
        response.set_cookie(key, 'true')
        return response


class BlogTypeView(View):
    def get(self, request):
        blog_all_list = Blog.objects.all()
        context = get_blog_list_attribute(request, blog_all_list)
        return render(request, 'blog_with_type.html', context)


class BlogDateView(View):
    def get(self, request):
        blogs_all_list = Blog.objects.all()
        context = get_blog_list_attribute(request, blogs_all_list)
        return render(request, 'blogs_with_date.html', context)
