from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.core.exceptions import PermissionDenied


from .models import Post, Category
from .forms import PostForm, CommentForm, ProfileForm


User = get_user_model()


def index(request):
    posts = Post.get_posts().annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')
    page_obj = Post.get_page_obj(request, posts)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'blog/index.html', context)


def post_detail(request, pk):
    if not request.user.is_authenticated:
        post = get_object_or_404(Post.get_posts(), pk=pk)
    else:
        post = get_object_or_404(
            Post.objects.select_related(
                'author',
                'location',
                'category'
            ).filter(
                Q(author=request.user) | (
                    Q(pub_date__lte=timezone.now())
                    & Q(is_published=True)
                    & Q(category__is_published=True)
                )
            ),
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
    posts = category.posts.select_related(
        'author',
        'location',
        'category'
    ).filter(
        is_published=True,
        pub_date__lte=timezone.now()
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')
    page_obj = Post.get_page_obj(request, posts)
    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, 'blog/category.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.select_related(
        'author',
        'location',
        'category'
    ).filter(author=user).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')
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
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=pk)


@login_required
def edit_comment(request, post_pk, comment_pk):
    post = get_object_or_404(Post, pk=post_pk)
    comment = get_object_or_404(
        post.comments.all(),
        pk=comment_pk
    )
    if comment.author != request.user:
        raise PermissionDenied
    form = CommentForm(request.POST or None,
                       instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', pk=post_pk)
    context = {
        'form': form,
        'comment': comment
    }
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_pk, comment_pk):
    post = get_object_or_404(Post, pk=post_pk)
    comment = get_object_or_404(
        post.comments.all(),
        pk=comment_pk
    )
    if comment.author != request.user:
        raise PermissionDenied
    context = {
        'comment': comment
    }
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
