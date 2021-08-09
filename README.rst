=====
Comments
=====

Comments is a Django app to to collect comments from users.

Authentication is required to access all endpoints and the app is intented 
for use via RESTful requests rather than being statically rendered.

Saying that, there is the ``{% render_comment_list for [app].[model] [object_id] %}`` template tag and default 
template that will render the comments for the current content_object.

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
4. Reivew ``permissions.py`` and define the appropriate class in your application to provide fine-grain control of endpoint permissions
5. Check out ``public`` and ``example`` apps for more info including basic JS/AJAX implementation.
