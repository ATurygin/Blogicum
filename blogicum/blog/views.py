from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import Post, Category
from .forms import PostForm, CommentForm, ProfileForm
from .utils import get_comment_for_update


User = get_user_model()


def index(request):
    posts = Post.post_set.with_relations().published() \
                .with_comments().ordered()
    page_obj = Post.get_page_obj(request, posts)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'blog/index.html', context)


def post_detail(request, pk):
    if not request.user.is_authenticated:
        post = get_object_or_404(
            Post.post_set.with_relations().published(),
            pk=pk
        )
    else:
        post = get_object_or_404(
            Post.post_set.with_relations().from_author(
                request.user
            ) | Post.post_set.with_relations().published(),
            pk=pk
        )
    context = {'post': post}
    context['form'] = CommentForm()
    context['comments'] = post.comments.select_related('author')
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category.objects.filter(
            is_published=True
        ),
        slug=category_slug
    )
    posts = Post.post_set.filter(category=category) \
                .with_relations().published() \
                .with_comments().ordered()
    page_obj = Post.get_page_obj(request, posts)
    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, 'blog/category.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.post_set.with_relations().from_author(user) \
                .with_comments().ordered()
    page_obj = Post.get_page_obj(request, posts)
    context = {
        'profile': user,
        'page_obj': page_obj
    }
    return render(request, 'blog/profile.html', context)


@login_required
def create_post(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.author = request.user
        instance.save()
        return redirect('blog:profile',
                        username=request.user.username)
    context = {'form': form}
    return render(request, 'blog/create.html', context)


def edit_post(request, pk):
    instance = get_object_or_404(Post, pk=pk)
    if (not request.user.is_authenticated
            or instance.author != request.user):
        return redirect('blog:post_detail', pk=pk)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=instance)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', pk=pk)
    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def delete_post(request, pk):
    instance = get_object_or_404(Post, pk=pk)
    if instance.author != request.user:
        raise PermissionDenied
    form = PostForm(instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:index')
    return render(request, 'blog/create.html', context)


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=pk)


@login_required
def edit_comment(request, post_pk, comment_pk):
    comment = get_comment_for_update(request, post_pk, comment_pk)
    context = {'comment': comment}
    form = CommentForm(request.POST or None,
                       instance=comment)
    context['form'] = form
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', pk=post_pk)
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_pk, comment_pk):
    comment = get_comment_for_update(request, post_pk, comment_pk)
    context = {'comment': comment}
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', pk=post_pk)
    return render(request, 'blog/comment.html', context)


@login_required
def edit_profile(request):
    form = ProfileForm(request.POST or None,
                       instance=request.user)
    context = {'form': form}
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user)
    return render(request, 'blog/user.html', context)
