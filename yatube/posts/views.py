from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow


def paginator(page_number, post_list):
    post = Paginator(post_list, settings.NUMBER_POST)
    page_obj = post.get_page(page_number)
    return page_obj


def index(request):
    post_list = cache.get('index_page')
    if not post_list:
        post_list = Post.objects.select_related('author', 'group')
        cache.set('index_page', post_list, 20)
    context = {
        'page_obj': paginator(request.GET.get('page'), post_list),
        'title': 'Последние обновления на сайте',
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author')
    context = {
        'group': group,
        'page_obj': paginator(request.GET.get('page'), post_list),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    post_author = get_object_or_404(User, username=username)
    post_list = post_author.posts.select_related('group')
    following = (request.user.is_authenticated
                 and post_author.following.filter(user=request.user).exists())
    context = {
        'page_obj': paginator(request.GET.get('page'), post_list),
        'count_post': post_list.count,
        'author': post_author,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'), pk=post_id
    )
    context = {
        'post': post,
        'count_post': post.author.posts.count(),
        'form': CommentForm(),
        'comments': post.comments.select_related('author')
    }
    return render(request, 'posts/post_detail.html', context, )


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author)

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author'), pk=post_id
    )
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)

    return render(request, 'posts/create_post.html',
                  {'form': form, 'is_edit': True})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.select_related('author', 'group').filter(
        author__following__user=request.user
    )
    context = {
        'page_obj': paginator(request.GET.get('page'), post_list),
        'title': 'Подписки на любимых авторов',
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username)
