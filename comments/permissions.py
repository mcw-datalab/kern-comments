class RootPerms:
    def can_list_comments(self, request, content_type, object_pk):
        return False

    def can_create_comment(self, request, content_type, object_pk):
        return False


class DetailPerms:
    def can_get_comment(self, request, content_type, object_pk):
        return False

    def can_update_comment(self, request, content_type, object_pk):
        return False

    def can_delete_comment(self, request, content_type, object_pk):
        return False


class PermissionRegistry:
    RootPermissions = RootPerms
    DetailPermissions = DetailPerms


_Registry = PermissionRegistry()


def get_registry():
    return _Registry
