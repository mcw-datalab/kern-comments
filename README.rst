=====
Comments
=====

Comments is a Django app to to collect comments from users.

Quick start
-----------

1. Add "comments" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'comments',
    ]

2. Include the comments URLconf in your project urls.py like this::

    path('comments/', include('comments.urls')),

3. Run ``python manage.py migrate`` to create the comment models.
