from django.apps import AppConfig


class PublicConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "public"

    def ready(self):
        from .permissions import init_permissions

        init_permissions()
