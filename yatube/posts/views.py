from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


def index(request):
    """Возвращает http-ответ с N последними публикациями."""
    paginated_posts = Paginator(
        Post.objects
        .select_related('author')
        .select_related('group'),
        settings.NUM_OF_POSTS_ON_PAGE
    )
    page_obj = paginated_posts.get_page(request.GET.get('page'))
    return render(request, 'posts/index.html',
                  {'title': 'Главная страница проекта yaTube',
                   'page_obj': page_obj,
                   'group_link_is_visible': True})


def profile(request, username):
    """Профиль пользователя с его публикациями."""
    author = User.objects.get(username=username)
    paginated_posts = Paginator(
        author.posts.select_related('group').all(),
        settings.NUM_OF_POSTS_ON_PAGE
    )
    page_obj = paginated_posts.get_page(request.GET.get('page'))
    context = {
        'page_obj': page_obj,
        'author': author,
        'group_link_is_visible': True
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Подробная информация о публикации."""
    post_queryset = (
        Post.objects
        .filter(id=post_id)
        .select_related('group')
        .select_related('author')
    )
    post = get_object_or_404(post_queryset)
    num_posts = Post.objects.filter(author_id=post.author_id).count()
    context = {
        'post': post,
        'num_posts': num_posts
    }
    return render(request, 'posts/post_detail.html', context)


def group_posts(request, slug):
    """
    Возвращает http-ответ с N последними публикациями определённой группы.
    """
    group = get_object_or_404(Group, slug=slug)
    paginated_posts = Paginator(
        group.posts
        .select_related('author'),
        settings.NUM_OF_POSTS_ON_PAGE
    )
    page_obj = paginated_posts.get_page(request.GET.get('page'))
    return render(request, 'posts/group_list.html',
                  {'group': group,
                   'page_obj': page_obj,
                   'group_link_is_visible': False})


@login_required
def post_create(request):
    """Функция обеспечивает создания публикации."""
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post_inst = form.save(commit=False)
            post_inst.author = request.user
            post_inst.save()
            return redirect('posts:profile', username=request.user.username)
        else:
            return render(request, 'posts/create_post.html', {'form': form})
    form = PostForm()
    return render(request, 'posts/create_post.html',
                  {'form': form,
                   'is_edit': False})


@login_required
def post_edit(request, post_id):
    """Функция обеспечивает редактирование публикации."""
    post = Post.objects.get(pk=post_id)
    if request.user.id != post.author_id:
        return redirect('posts:post_detail', post_id=post_id)
    if request.method == 'POST':
        form = PostForm(instance=post, data=request.POST)
        if form.is_valid():
            form.save()
        else:
            return render(request, 'posts/create_post.html',
                          {'post_id': post_id,
                           'form': form,
                           'is_edit': True})
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(instance=post)
    return render(request, 'posts/create_post.html',
                  {'post_id': post_id,
                   'form': form,
                   'is_edit': True})
