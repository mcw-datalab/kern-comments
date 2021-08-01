from importlib import import_module

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class RootPerms:
    def can_list_comments(self, request, content_type, object_pk):
        return False

    def can_create_comment(self, request, content_type, object_pk):
        return False


class DetailPerms:
    def can_get_comment(self, request, content_type, object_pk, comment_id):
        return False

    def can_update_comment(self, request, content_type, object_pk, comment_id):
        return False

    def can_delete_comment(self, request, content_type, object_pk, comment_id):
        return False


COMMENT_ROOT_PERMISSIONS = getattr(settings, "COMMENT_ROOT_PERMISSIONS", RootPerms)
COMMENT_DETAIL_PERMISSIONS = getattr(
    settings, "COMMENT_DETAIL_PERMISSIONS", DetailPerms
)


class PermissionRegistry:
    def __init__(self):
        self.RootPermissions = self._import_class(COMMENT_ROOT_PERMISSIONS)
        self.DetailPermissions = self._import_class(COMMENT_DETAIL_PERMISSIONS)

    def _import_class(self, klass):
        if callable(klass):
            return klass
        try:
            mod_name, func_name = self._split_module_path(klass)
            mod = import_module(mod_name)
            return getattr(mod, func_name)
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
