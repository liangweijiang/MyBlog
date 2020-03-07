from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.db.models import ObjectDoesNotExist
from .models import LikeCount, LikeRecord


# Create your views here.
def ErrorResponse(code, message):
    data = {}
    data['status'] = 'ERROR'
    data['code'] = code
    data['message'] = message
    return JsonResponse(data)


def SuccessResponse(like_count):
    data = {}
    data['status'] = 'SUCCESS'
    data['like_count'] = like_count
    return JsonResponse(data)


def like_change(request):
    user = request.user
    # 先判断用户是否登录
    if not user.is_authenticated:
        return ErrorResponse(400, 'you were not login')
    content_type = request.GET.get('content_type')
    object_id = int(request.GET.get('object_id'))
    is_like = request.GET.get('is_like')
    try:
        content_type = ContentType.objects.get(model=content_type)
    except ObjectDoesNotExist:
        return ErrorResponse(401, 'object not exist')

    # 对数据进行处理

    if is_like == 'true':
        # 证明该用户在该评论或文章下面想要点赞
        like_record, created = LikeRecord.objects.get_or_create(content_type=content_type, object_id=object_id,
                                                                user=user)
        if created:
            # 证明用户以前没有点过赞
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
            like_count.like_count += 1
            like_count.save()
            return SuccessResponse(like_count.like_count)
        else:
            return ErrorResponse(402, 'you were liked')
    else:
        if LikeRecord.objects.filter(content_type=content_type, object_id=object_id, user=user).exists():
            # 有点赞过，取消点赞
            like_record = LikeRecord.objects.get(content_type=content_type, object_id=object_id, user=user)
            like_record.delete()
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
            if not created:
                like_count.like_count -= 1
                like_count.save()
                return SuccessResponse(like_count.like_count)
            else:
                return ErrorResponse(404, 'data error')
        else:
            # 没有点赞过，不能取消
            return ErrorResponse(403, 'you were not liked')
