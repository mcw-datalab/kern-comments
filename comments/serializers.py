from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Model, QuerySet
from django.forms import model_to_dict


class ExtendedEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, Model):
            return model_to_dict(o)
        if isinstance(o, QuerySet):
            return [model_to_dict(x) for x in o]
        return super().default(o)
