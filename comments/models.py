from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _


COMMENT_MAX_LENGTH = getattr(settings, "COMMENT_MAX_LENGTH", 3000)


class BaseCommentAbstractModel(models.Model):
    """
    An abstract base class that any custom comment models probably should
    subclass.
    """

    # Content-object field
    content_type = models.ForeignKey(
        ContentType,
        verbose_name=_("content type"),
        related_name="content_type_set_for_%(class)s",
        on_delete=models.CASCADE,
    )
    object_pk = models.CharField(_("object ID"), db_index=True, max_length=64)
    content = GenericForeignKey(ct_field="content_type", fk_field="object_pk")

    class Meta:
        abstract = True


class CommentQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def for_model(self, model):
        """
        QuerySet for all comments for a particular model (either an instance or
        a class).
        """
        ct = ContentType.objects.get_for_model(model)
        queryset = self.filter(content_type=ct)
        if isinstance(model, models.Model):
            return queryset.filter(object_pk=force_str(model._get_pk_val()))
        return queryset


class CommentManager(models.Manager):
    def get_queryset(self):
        return CommentQuerySet(self.model, using=self._db)


class Comment(BaseCommentAbstractModel):

    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, related_name="child_comments"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("user"),
        blank=True,
        null=False,
        related_name="%(class)s_comments",
        on_delete=models.CASCADE,
    )
    comment = models.TextField(_("comment"), max_length=COMMENT_MAX_LENGTH)
    creation_date = models.DateTimeField(auto_now_add=True)
    modifed_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    objects = CommentManager()

    class Meta:
        ordering = ("creation_date",)
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")

    def get_content_object_url(self):
        """
        Get a URL suitable for redirecting to the content object.
        """
        return reverse(
            "comments-url-redirect", args=(self.content_type_id, self.object_pk)
        )
