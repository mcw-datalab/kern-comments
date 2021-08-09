import json

from django.http import HttpResponse, JsonResponse, HttpResponseNotModified
from django.shortcuts import get_object_or_404
from django.views import View

import bleach

from .models import Comment
from .target import get_content_type_and_target_or_none
from .permissions import get_registry
from .serializers import ExtendedEncoder


def _sanitize_and_linkify(text, **clean_kwargs):
    text = bleach.clean(text, **clean_kwargs)
    return bleach.linkify(text)


def _build_error_response(message, status):
    return JSONResponse({"error": str(message)}, status=status)


class JSONResponse(JsonResponse):
    def __init__(
        self,
        data,
        encoder=ExtendedEncoder,
        safe=False,
        json_dumps_params=None,
        **kwargs
    ):
        super().__init__(data, encoder, safe, json_dumps_params, **kwargs)


class CommentView(View):

    perms = get_registry().RootViewPermissions

    def get(self, request, *args, **kwargs):
        content_type = kwargs["content_type"]
        object_pk = kwargs["object_pk"]

        # check permission before doing any processing
        if not self.perms.can_list_comments(request, content_type, object_pk):
            return _build_error_response("Permission denied", 403)  # forbidden

        content_type, target = get_content_type_and_target_or_none(
            content_type, object_pk
        )
        if target is None:
            return _build_error_response("Bad content type or object id", 404)

        comments = Comment.objects.for_model(target).active()
        return JSONResponse(comments)

    def post(self, request, *args, **kwargs):
        content_type_id = kwargs["content_type"]
        object_pk = kwargs["object_pk"]

        # check permission before doing any processing
        if not self.perms.can_create_comment(request, content_type_id, object_pk):
            return _build_error_response("Permission denied", 403)  # forbidden

        content_type, target = get_content_type_and_target_or_none(
            content_type_id, object_pk
        )
        if target is None:
            return _build_error_response("Bad content type or object id", 404)

        body = json.loads(request.body)
        # do this first so we don't need to check len until after sanitization
        body["comment"] = _sanitize_and_linkify(body.get("comment", ""))

        # validated against schema
        is_valid, err = Comment.validate_json(body)
        if not is_valid:
            return _build_error_response(err, 400)  # bad request

        parent = None
        parent_id = body.get("parentID", None)
        if parent_id is not None:
            parent = Comment.objects.for_model(target).filter(id=parent_id).first()
            if parent is None:
                return _build_error_response("Bad parent", 404)

        instance = Comment.objects.create(
            content_type=content_type,
            object_pk=object_pk,
            user=request.user,
            parent=parent,
            comment=body["comment"],
        )
        return JSONResponse(instance)


class CommentDetailView(View):

    perms = get_registry().DetailViewPermissions

    def get(self, request, *args, **kwargs):
        content_type = kwargs["content_type"]
        object_pk = kwargs["object_pk"]
        comment_id = kwargs["comment_id"]

        # check permission
        if not self.perms.can_get_comment(request, content_type, object_pk, comment_id):
            return _build_error_response("Permission denied", 403)  # forbidden

        comment = get_object_or_404(Comment.objects.active(), pk=comment_id)
        return JSONResponse(comment)

    def put(self, request, *args, **kwargs):
        content_type = kwargs["content_type"]
        object_pk = kwargs["object_pk"]
        comment_id = kwargs["comment_id"]

        # check permission
        if not self.perms.can_update_comment(
            request, content_type, object_pk, comment_id
        ):
            return _build_error_response("Permission denied", 403)  # forbidden

        comment = get_object_or_404(
            Comment.objects.active(), pk=comment_id, user=request.user
        )

        # validated against schema
        body = json.loads(request.body)
        is_valid, err = Comment.validate_json(body)
        if not is_valid:
            return _build_error_response(err, 400)  # bad request

        # do this first so we don't need to check len until after sanitization
        text = _sanitize_and_linkify(body.get("comment", ""))
        if text:
            comment.comment = text
            comment.save()
            return JSONResponse(comment)
        else:
            return HttpResponseNotModified()

    def delete(self, request, *args, **kwargs):
        content_type = kwargs["content_type"]
        object_pk = kwargs["object_pk"]
        comment_id = kwargs["comment_id"]

        # check permission
        if not self.perms.can_get_comment(request, content_type, object_pk, comment_id):
            return _build_error_response("Permission denied", 403)  # forbidden

        comment = get_object_or_404(
            Comment.objects.active(), pk=comment_id, user=request.user
        )
        comment.is_active = False
        comment.save()
        return HttpResponse(status=204)  # no content
