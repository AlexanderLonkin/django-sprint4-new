from django.shortcuts import render


def page_not_found(request, exception):
    """Отобразить пользовательскую страницу ошибки 404."""
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    """Отобразить пользовательскую страницу ошибки CSRF."""
    return render(request, 'pages/403csrf.html', status=403)


def server_error(request):
    """Отобразить пользовательскую страницу ошибки 500."""
    return render(request, 'pages/500.html', status=500)
