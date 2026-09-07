from django.db import models
from django.db.models import Count
from django.utils import timezone

MAX_LENGTH_FIELDS = 256


class BaseModel(models.Model):
    """Абстрактная модель с признаком публикации и датой создания."""

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено',
    )

    class Meta:
        abstract = True


class Category(BaseModel):
    """Категория, объединяющая тематически связанные публикации."""

    title = models.CharField(
        max_length=MAX_LENGTH_FIELDS,
        verbose_name='Заголовок',
    )
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; разрешены символы '
            'латиницы, цифры, дефис и подчёркивание.'
        ),
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        """Вернуть заголовок категории."""
        return self.title


class Location(BaseModel):
    """Место, указанное автором публикации."""

    name = models.CharField(
        max_length=MAX_LENGTH_FIELDS,
        verbose_name='Название места',
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        """Вернуть название места."""
        return self.name


class PostQuerySet(models.QuerySet):
    """Набор запросов с общими правилами выборки публикаций."""

    def published(self):
        """Оставить публикации, доступные всем посетителям."""
        return self.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        )

    def for_list(self):
        """Добавить связанные данные и количество комментариев."""
        return self.select_related(
            'author', 'category', 'location'
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')


class Post(BaseModel):
    """Публикация пользователя с категорией и местоположением."""

    title = models.CharField(
        max_length=MAX_LENGTH_FIELDS,
        verbose_name='Заголовок',
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
        ),
    )
    author = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
    )
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    objects = PostQuerySet.as_manager()

    class Meta:
        default_related_name = 'posts'
        ordering = ('-pub_date',)
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        """Вернуть заголовок публикации."""
        return self.title


class Comment(models.Model):
    """Комментарий пользователя к публикации."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(verbose_name='Текст')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено',
    )

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        """Вернуть сокращённый текст комментария."""
        return self.text[:30]
