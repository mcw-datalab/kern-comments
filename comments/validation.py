import bleach


def sanitize_and_linkify(text, **clean_kwargs):
    text = bleach.clean(text, **clean_kwargs)
    return bleach.linkify(text)
