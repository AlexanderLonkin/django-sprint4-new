from django.contrib import admin

from .models import Category, Comment, Location, Post


class CategoryAdmin(admin.ModelAdmin):
    """Настройки отображения категорий в панели администратора."""

    list_display = ('title', 'description', 'slug')


class LocationAdmin(admin.ModelAdmin):
    """Настройки отображения мест в панели администратора."""

    list_display = ('name',)


class PostAdmin(admin.ModelAdmin):
    """Настройки отображения публикаций в панели администратора."""

    list_display = ('title', 'author', 'created_at', 'is_published')


class CommentAdmin(admin.ModelAdmin):
    """Настройки отображения комментариев в панели администратора."""

    list_display = ('post', 'author', 'text', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text', 'author__username', 'post__title')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
