from django.contrib.contenttypes.views import shortcut
from django.urls import path, re_path

from .views.comments import post_comment, comment_done
from .views.moderation import (
    flag,
    flag_done,
    delete,
    delete_done,
    approve,
    approve_done,
)


urlpatterns = [
    path("post/", add_comment, name="comments_add"),
    path("post/<int:parent_comment_id>/", add_comment, name="comments_add"),
    path("delete/<int:comment_id>/", delete_comment, name="comments_delete"),
    re_path(r"^cr/(\d+)/(.+)/$", shortcut, name="comment_url_redirect"),
]
