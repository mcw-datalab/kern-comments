from django import forms
from django.utils.crypto import salted_hmac, constant_time_compare
from django.utils.translation import gettext_lazy as _

import bleach

from .models import COMMENT_MAX_LENGTH


ALLOWED_TAGS = [
    "a",
    "b",
    "blockquote",
    "code",
    "em",
    "i",
    "li",
    "ol",
    "strong",
    "ul",
]


#: Map of allowed attributes by tag
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
}


class CommentForm(forms.Form):
    content_type = forms.CharField(widget=forms.HiddenInput, required=True)
    object_pk = forms.CharField(widget=forms.HiddenInput, required=True)
    parent_id = forms.CharField(widget=forms.HiddenInput, required=False)
    security_hash = forms.CharField(
        min_length=40, max_length=40, widget=forms.HiddenInput
    )

    comment = forms.CharField(
        label=_("Comment"),
        widget=forms.Textarea,
        max_length=COMMENT_MAX_LENGTH,
        required=True,
    )

    def __init__(self, target_object, data=None, initial=None, **kwargs):
        if initial is None:
            initial = {}
        initial.update(self._generate_initial_hash(target_object))
        super().__init__(data=data, initial=initial, **kwargs)

    def _generate_initial_hash(self, target_object):
        data = {
            "content_type": str(target_object._meta),
            "object_pk": str(target_object._get_pk_val()),
        }
        data["security_hash"] = self._generate_security_hash(data)
        return data

    def _generate_security_hash(self, data):
        key_salt = "comments.forms.CommentForm"
        value = "-".join(data.values())
        return salted_hmac(key_salt, value).hexdigest()

    def clean_security_hash(self):
        data = {
            "content_type": self.data.get("content_type", ""),
            "object_pk": self.data.get("object_pk", ""),
        }
        expected = self._generate_security_hash(data)
        actual = self.cleaned_data["security_hash"]
        if not constant_time_compare(expected, actual):
            raise forms.ValidationError("Security hash check failed.")
        return actual

    def clean_comment(self):
        comment = self.data.get("comment", "")
        comment = bleach.clean(
            comment, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES
        )
        return bleach.linkify(comment)
