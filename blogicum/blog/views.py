from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.constants import POSTS_PER_PAGE

from .forms import CommentForm, PostForm, UserEditForm
from .models import Category, Comment, Post

User = get_user_model()


def get_posts_queryset(apply_filters=False, annotate_comments=False):
    """Вернуть публикации со связанными объектами и числом комментариев."""
    queryset = Post.objects.select_related('author', 'location', 'category')
    if apply_filters:
        queryset = queryset.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )
    if annotate_comments:
        queryset = queryset.annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
    return queryset


def paginate_queryset(request, queryset):
    """Вернуть запрошенную страницу переданного набора объектов."""
    paginator = Paginator(queryset, POSTS_PER_PAGE)
    return paginator.get_page(request.GET.get('page'))


def index(request):
    """Показать страницу с лентой последних публикаций."""
    page_obj = paginate_queryset(
        request,
        get_posts_queryset(apply_filters=True, annotate_comments=True),
    )
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, post_id):
    """Показать публикацию и связанные с ней комментарии."""
    post = get_object_or_404(get_posts_queryset(), pk=post_id)
    if post.author != request.user and (
        not post.is_published
        or post.category is None
        or not post.category.is_published
        or post.pub_date > timezone.now()
    ):
        raise Http404
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
    page_obj = paginate_queryset(
        request,
        get_posts_queryset(
            apply_filters=True,
            annotate_comments=True,
        ).filter(category=category),
    )
    return render(request, 'blog/category.html', {
        'category': category, 'page_obj': page_obj,
    })


def profile_view(request, username):
    """Показать профиль пользователя и доступные публикации автора."""
    profile_user = get_object_or_404(User, username=username)
    if request.user == profile_user:
        queryset = get_posts_queryset(annotate_comments=True)
    else:
        queryset = get_posts_queryset(
            apply_filters=True,
            annotate_comments=True,
        )
    queryset = queryset.filter(author=profile_user)
    page_obj = paginate_queryset(request, queryset)
    return render(request, 'blog/profile.html', {
        'profile': profile_user,
        'page_obj': page_obj,
    })


@login_required
def edit_profile(request):
    """Изменить профиль вошедшего пользователя."""
    form = UserEditForm(request.POST or None, instance=request.user)
    if form.is_valid():
        user = form.save()
        return redirect('blog:profile', username=user.username)
    return render(request, 'blog/user.html', {'form': form})


@login_required
def create_post(request):
    """Создать публикацию от имени вошедшего пользователя."""
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    """Изменить публикацию, если пользователь является её автором."""
    post = get_object_or_404(get_posts_queryset(), pk=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None, request.FILES or None, instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    """Удалить публикацию после подтверждения её автором."""
    post = get_object_or_404(get_posts_queryset(), pk=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'post': post})


@login_required
def add_comment(request, post_id):
    """Добавить комментарий вошедшего пользователя к публикации."""
    post = get_object_or_404(get_posts_queryset(), pk=post_id)
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


@login_required
def edit_comment(request, post_id, comment_id):
    """Изменить принадлежащий пользователю комментарий."""
    comment = get_object_or_404(
        Comment, pk=comment_id, post_id=post_id
    )
    if comment.author != request.user:
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
    comment = get_object_or_404(
        Comment, pk=comment_id, post_id=post_id
    )
    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', {'comment': comment})
