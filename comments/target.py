from django.contrib.contenttypes.models import ContentType


def get_content_type_and_target_or_none(content_type_id, object_pk):
    try:
        content_type = ContentType.objects.get_for_id(content_type_id)
        model = content_type.model_class()
        return content_type, model._default_manager.get(pk=object_pk)
    except Exception:
        return None, None
