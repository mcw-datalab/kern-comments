from django.urls import path

from .views import CommentView, CommentDetailView


urlpatterns = [
    path(
        "/<int:content_type>/<int:object_pk>/",
        CommentView.as_view(),
        name="comment",
    ),
    path(
        "/<int:content_type>/<int:object_pk>/<int:comment_id>/",
        CommentDetailView.as_view(),
        name="comments_detail",
    ),
]
