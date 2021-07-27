from django.apps import apps


def get_target_model_name(content_type):
    return content_type.split(".", 1)


def get_target_model(content_type):
    return apps.get_model(*get_target_model_name(content_type))


def get_target_object_or_none(content_type, object_pk):
    try:
        model = get_target_model(content_type)
        return model._default_manager.get(pk=object_pk)
    except Exception:
        return None
