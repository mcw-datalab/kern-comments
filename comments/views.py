import json

from django.http import HttpResponse, JsonResponse, HttpResponseNotModified
from django.shortcuts import get_object_or_404
from django.views import View

import bleach

from .models import Comment
from .target import get_target_object_or_none


def _sanitize_and_linkify(text, **clean_kwargs):
    text = bleach.clean(text, **clean_kwargs)
    return bleach.linkify(text)


def _build_error_response(message, status):
    return JsonResponse({"error": message}, status=404)


class CommentView(View):
    def get(self, request, *args, **kwargs):
        content_type = kwargs["content_type"]
        object_pk = kwargs["object_pk"]

        # check permission before doing any processing
        if not self.can_list_comments(request, content_type, object_pk):
            return _build_error_response("Permission denied", 403)  # forbidden

        target = get_target_object_or_none(content_type, object_pk)
        if target is None:
            return _build_error_response("Bad content type or object id", 404)

        comments = Comment.objects.for_model(target).active().all()
        return JsonResponse(comments)

    def post(self, request, *args, **kwargs):
        content_type = kwargs["content_type"]
        object_pk = kwargs["object_pk"]

        # check permission before doing any processing
        if not self.can_create_comment(request, content_type, object_pk):
            return _build_error_response("Permission denied", 403)  # forbidden

        target = get_target_object_or_none(content_type, object_pk)
        if target is None:
            return _build_error_response("Bad content type or object id", 404)

        body = json.loads(request.body)
        # do this first so we don't need to check len until after sanitization
        body["comment"] = _sanitize_and_linkify(body.get("comment", ""))

        is_valid, err = Comment.validate_json(body)
        if not is_valid:
            return _build_error_response(err, 400)  # bad request

        parent = None
        parent_id = body.get("parent_id", None)
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
        return JsonResponse(instance)

    def can_create_comment(self, request, content_type, object_pk):
        """Subclasses should override this"""
        return False

    def can_list_comments(self, request, content_type, object_pk):
        return False


class CommentDetailView(View):
    def get(self, request, *args, **kwargs):
        content_type = kwargs["content_type"]
        object_pk = kwargs["object_pk"]
        comment_id = kwargs["comment_id"]

        # check permission
        if not self.can_get_comment(request, content_type, object_pk, comment_id):
            return _build_error_response("Permission denied", 403)  # forbidden

        comment = get_object_or_404(Comment.objects.active(), pk=comment_id)
        return JsonResponse(comment)

    def put(self, request, *args, **kwargs):
        content_type = kwargs["content_type"]
        object_pk = kwargs["object_pk"]
        comment_id = kwargs["comment_id"]

        # check permission
        if not self.can_get_comment(request, content_type, object_pk, comment_id):
            return _build_error_response("Permission denied", 403)  # forbidden

        comment = get_object_or_404(
            Comment.objects.active(), pk=kwargs["pk"], user=request.user
        )
        body = json.loads(request.body)
        # do this first so we don't need to check len until after sanitization
        text = _sanitize_and_linkify(body.get("comment", ""))
        if text:
            comment.comment = text
            comment.save()
            return JsonResponse(comment)
        else:
            return HttpResponseNotModified()

    def delete(self, request, *args, **kwargs):
        content_type = kwargs["content_type"]
        object_pk = kwargs["object_pk"]
        comment_id = kwargs["comment_id"]

        # check permission
        if not self.can_get_comment(request, content_type, object_pk, comment_id):
            return _build_error_response("Permission denied", 403)  # forbidden

        comment = get_object_or_404(
            Comment.objects.active(), pk=kwargs["pk"], user=request.user
        )
        comment.is_active = False
        comment.save()
        return HttpResponse(status=204)  # no content

    def can_get_comment(self, request, content_type, object_pk, comment_id):
        """Subclasses should override this"""
        return False

    def can_update_comment(self, request, content_type, object_pk, comment_id):
        """Subclasses should override this"""
        return False

    def can_delete_comment(self, request, content_type, object_pk, comment_id):
        """Subclasses should override this"""
        return False
