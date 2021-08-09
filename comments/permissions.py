from importlib import import_module

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class CommentViewPermissions:
    """Permissions applied to CommentView"""

    def can_list_comments(self, request, content_type, object_pk):
        return False

    def can_create_comment(self, request, content_type, object_pk):
        return False


class CommentDetailViewPermissions:
    def can_get_comment(self, request, content_type, object_pk, comment_id):
        return False

    def can_update_comment(self, request, content_type, object_pk, comment_id):
        return False

    def can_delete_comment(self, request, content_type, object_pk, comment_id):
        return False


COMMENT_VIEW_PERMISSIONS = getattr(
    settings, "COMMENT_VIEW_PERMISSIONS", CommentViewPermissions
)
COMMENT_DETAIL_VIEW_PERMISSIONS = getattr(
    settings, "COMMENT_DETAIL_VIEW_PERMISSIONS", CommentDetailViewPermissions
)


class PermissionRegistry:
    def __init__(self):
        self.RootViewPermissions = self._import_class(COMMENT_VIEW_PERMISSIONS)
        self.DetailViewPermissions = self._import_class(COMMENT_DETAIL_VIEW_PERMISSIONS)

    def _import_class(self, klass):
        if callable(klass):
            return klass
        try:
            mod_name, func_name = self._split_module_path(klass)
            mod = import_module(mod_name)
            return getattr(mod, func_name)()
        except ImportError as e:
            raise ImproperlyConfigured(f"{klass} refers to a non-existent package: {e}")
        raise ImproperlyConfigured("klass must be a string or callable")

    def _split_module_path(self, path):
        try:
            dot = path.rindex(".")
        except ValueError:
            return path, ""
        return path[:dot], path[dot + 1 :]


_Registry = PermissionRegistry()


def get_registry():
    return _Registry
