from django.contrib import admin

from .models import Category, Location, Post


class CategoryAdmin(admin.ModelAdmin):
    """Настройки отображения категорий в панели администратора."""

    list_display = ('title', 'description', 'slug')


class LocationAdmin(admin.ModelAdmin):
    """Настройки отображения мест в панели администратора."""

    list_display = ('name',)


class PostAdmin(admin.ModelAdmin):
    """Настройки отображения публикаций в панели администратора."""

    list_display = ('title', 'author', 'created_at', 'is_published')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
