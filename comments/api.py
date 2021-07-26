import json

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_POST, require_GET

from .models import Comment
from .forms import CommentForm


@require_POST
def add_comment(request, parent_comment_id=None):
    data = json.loads(request.body)
    ctype = data.get("content_type")
    object_pk = data.get("object_pk")

    try:
        model = apps.get_model(*ctype.split(".", 1))
        target = model._default_manager.get(pk=object_pk)
    except Exception:
        return HttpResponseBadRequest("Invalid content type or object")

    form = CommentForm(target, data=data)
    if form.is_valid():
        comment = Comment(
            content_type=ContentType.objects.get_for_model(target),
            object_pk=str(target._get_pk_val()),
            user=request.user,
            comment=form.cleaned_data["comment"],
        )
        # set parent
        if parent_comment_id is not None:
            comment.parent = Comment.objects.get(id=parent_comment_id)
        comment.save()
        return JsonResponse()
    else:
        JsonResponse(data=form.errors)
