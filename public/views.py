from django.shortcuts import render

from .models import Post


def index(request):
    post = Post.objects.first()
    return render(request, "index.html", {"user": request.user, "post": post})
