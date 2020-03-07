from django.http import JsonResponse, HttpResponse
from .models import Comment
from .forms import CommentForm
from django.contrib.contenttypes.models import ContentType


def update_comment(request):
    # referer = request.META.get('HTTP_REFERER', reverse('index'))
    comment_form = CommentForm(request.POST, user=request.user)
    data = {}
    if comment_form.is_valid():
        comment = Comment()
        comment.user = comment_form.cleaned_data['user']
        comment.text = comment_form.cleaned_data['text']
        comment.content_object = comment_form.cleaned_data['content_object']
        parent = comment_form.cleaned_data['parent']
        if parent:
            comment.root = parent.root if parent.root else parent
            comment.parent = parent
            data['reply_to'] = parent.user.username
        else:
            data['reply_to'] = ''
        comment.save()
        # 发送邮件通知
        mail_status = comment.send_email()
        if mail_status == False:
            data['mail_mes'] = '你还未绑定邮箱,绑定邮箱可以通知对方'
        # 发送信息给ajax
        data['status'] = 'SUCCESS'
        data['username'] = comment.user.username
        data['content_type'] = ContentType.objects.get_for_model(comment).model
        data['comment_time'] = comment.comment_time.strftime('%Y-%m-%d %H:%M:%S')
        data['text'] = comment.text
        data['pk'] = comment.pk
        data['root_pk'] = comment.root.pk if comment.root else ''
        if comment.root:
            data['reply_count'] = comment.root.root_comment.count()
        else:
            data['reply_count'] = 0

    else:
        # return render(request, 'error.html', {'message': comment_form.errors, 'redirect_to': referer})
        data['status'] = 'ERROR'
        data['message'] = list(comment_form.errors.values())[0][0]
    return JsonResponse(data)
