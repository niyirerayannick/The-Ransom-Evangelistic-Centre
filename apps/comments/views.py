from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from .forms import CommentForm
from apps.news.models import Post


@require_POST
def submit_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status="published")
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        if request.user.is_authenticated:
            comment.user = request.user
            comment.author_name = request.user.get_full_name() or request.user.username
            comment.author_email = request.user.email
            comment.status = "approved"
        comment.ip_address = request.META.get("REMOTE_ADDR", "")
        comment.save()
        messages.success(request, _("Your comment has been submitted."))
    return redirect(post.get_absolute_url())
