from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from .models import Post


def get_comment_for_update(request, post_pk, comment_pk):
    post = get_object_or_404(Post, pk=post_pk)
    comment = get_object_or_404(
        post.comments.all(),
        pk=comment_pk
    )
    if comment.author != request.user:
        raise PermissionDenied
    return comment
