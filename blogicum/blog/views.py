from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from core.constants import POSTS_PER_PAGE

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post


def published_posts():
    """Вернуть публикации, доступные всем посетителям сайта."""
    return Post.objects.published().for_list()


def index(request):
    """Показать страницу с лентой последних публикаций."""
    page_obj = Paginator(published_posts(), POSTS_PER_PAGE).get_page(
        request.GET.get('page')
    )
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, post_id):
    """Показать публикацию и связанные с ней комментарии."""
    available_posts = Post.objects.published()
    if request.user.is_authenticated:
        available_posts |= Post.objects.filter(author=request.user)
    post = get_object_or_404(
        available_posts.select_related('author', 'location', 'category'),
        pk=post_id,
    )
    return render(request, 'blog/detail.html', {
        'post': post,
        'comments': post.comments.select_related('author'),
        'form': CommentForm(),
    })


def category_posts(request, category_slug):
    """Показать опубликованные записи выбранной категории."""
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True
    )
    page_obj = Paginator(
        published_posts().filter(category=category), POSTS_PER_PAGE
    ).get_page(request.GET.get('page'))
    return render(request, 'blog/category.html', {
        'category': category, 'page_obj': page_obj,
    })


@login_required
def create_post(request):
    """Создать публикацию от имени вошедшего пользователя."""
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('users:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    """Изменить публикацию, если пользователь является её автором."""
    post = _owned_object(request, Post, pk=post_id)
    if post is None:
        return redirect('blog:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None, request.FILES or None, instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/create.html', {
        'form': form, 'action_type': 'update',
    })


@login_required
def delete_post(request, post_id):
    """Удалить публикацию после подтверждения её автором."""
    post = _owned_object(request, Post, pk=post_id)
    if post is None:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('users:profile', username=request.user.username)
    return render(request, 'blog/create.html', {
        'post': post, 'object': post, 'action_type': 'delete',
    })


@login_required
def add_comment(request, post_id):
    """Добавить комментарий вошедшего пользователя к публикации."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/detail.html', {
        'post': post,
        'comments': post.comments.select_related('author'),
        'form': form,
    })


def _owned_object(request, model, **lookup):
    """Вернуть объект, если он существует и принадлежит пользователю."""
    obj = get_object_or_404(model, **lookup)
    return obj if obj.author == request.user else None


@login_required
def edit_comment(request, post_id, comment_id):
    """Изменить принадлежащий пользователю комментарий."""
    comment = _owned_object(
        request, Comment, pk=comment_id, post_id=post_id
    )
    if comment is None:
        return redirect('blog:post_detail', post_id=post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', {
        'comment': comment, 'form': form,
    })


@login_required
def delete_comment(request, post_id, comment_id):
    """Удалить принадлежащий пользователю комментарий."""
    comment = _owned_object(
        request, Comment, pk=comment_id, post_id=post_id
    )
    if comment is None:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', {'comment': comment})
