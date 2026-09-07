from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from blog.models import Post
from core.constants import POSTS_PER_PAGE

from .forms import UserEditForm


def profile_view(request, username):
    """Показать профиль пользователя и доступные публикации автора."""
    profile = get_object_or_404(User, username=username)
    if request.user == profile:
        posts = Post.objects.filter(author=profile).for_list()
    else:
        posts = Post.objects.published().for_list().filter(
            author=profile
        )
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'profile': profile, 'page_obj': page_obj}
    return render(request, 'blog/profile.html', context)


@login_required
def profile_edit_view(request):
    """Изменить профиль вошедшего пользователя."""
    user = request.user

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)

        if form.is_valid():
            form.save()
            return redirect('users:profile', username=user.username)
    else:
        form = UserEditForm(instance=user)

    context = {
        'form': form,
        'profile_user': user,
    }
    return render(request, 'blog/user.html', context)
