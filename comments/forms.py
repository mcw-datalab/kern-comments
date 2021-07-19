import time

from django import forms
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.forms.utils import ErrorDict
from django.utils.crypto import salted_hmac, constant_time_compare
from django.utils.encoding import force_str
from django.utils.text import get_text_list
from django.utils import timezone
from django.utils.translation import pgettext_lazy, ngettext, gettext, gettext_lazy as _

from . import get_model

COMMENT_MAX_LENGTH = getattr(settings, "COMMENT_MAX_LENGTH", 3000)
DEFAULT_COMMENTS_TIMEOUT = getattr(settings, "COMMENTS_TIMEOUT", (2 * 60 * 60))  # 2h


class CommentSecurityForm(forms.Form):
    """
    Handles the security aspects (anti-spoofing) for comment forms.
    """

    content_type = forms.CharField(widget=forms.HiddenInput)
    object_pk = forms.CharField(widget=forms.HiddenInput)
    timestamp = forms.IntegerField(widget=forms.HiddenInput)
    security_hash = forms.CharField(
        min_length=40, max_length=40, widget=forms.HiddenInput
    )

    def __init__(self, target_object, data=None, initial=None, **kwargs):
        self.target_object = target_object
        if initial is None:
            initial = {}
        initial.update(self.generate_security_data())
        super().__init__(data=data, initial=initial, **kwargs)

    def security_errors(self):
        """Return just those errors associated with security"""
        errors = ErrorDict()
        for f in ["honeypot", "timestamp", "security_hash"]:
            if f in self.errors:
                errors[f] = self.errors[f]
        return errors

    def clean_security_hash(self):
        """Check the security hash."""
        security_hash_dict = {
            "content_type": self.data.get("content_type", ""),
            "object_pk": self.data.get("object_pk", ""),
            "timestamp": self.data.get("timestamp", ""),
        }
        expected_hash = self.generate_security_hash(**security_hash_dict)
        actual_hash = self.cleaned_data["security_hash"]
        if not constant_time_compare(expected_hash, actual_hash):
            raise forms.ValidationError("Security hash check failed.")
        return actual_hash

    def clean_timestamp(self):
        """Make sure the timestamp isn't too far (default is > 2 hours) in the past."""
        ts = self.cleaned_data["timestamp"]
        if time.time() - ts > DEFAULT_COMMENTS_TIMEOUT:
            raise forms.ValidationError("Timestamp check failed")
        return ts

    def generate_security_data(self):
        """Generate a dict of security data for "initial" data."""
        timestamp = int(time.time())
        security_dict = {
            "content_type": str(self.target_object._meta),
            "object_pk": str(self.target_object._get_pk_val()),
            "timestamp": str(timestamp),
            "security_hash": self.initial_security_hash(timestamp),
        }
        return security_dict

    def initial_security_hash(self, timestamp):
        """
        Generate the initial security hash from self.content_object
        and a (unix) timestamp.
        """

        initial_security_dict = {
            "content_type": str(self.target_object._meta),
            "object_pk": str(self.target_object._get_pk_val()),
            "timestamp": str(timestamp),
        }
        return self.generate_security_hash(**initial_security_dict)

    def generate_security_hash(self, content_type, object_pk, timestamp):
        """
        Generate a HMAC security hash from the provided info.
        """
        info = (content_type, object_pk, timestamp)
        key_salt = "kern-comments.CommentSecurityForm"
        value = "-".join(info)
        return salted_hmac(key_salt, value).hexdigest()
