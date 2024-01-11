from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.paginator import Paginator

from core.models import PublishedModel

User = get_user_model()


class Category(PublishedModel):
    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    slug = models.SlugField(
        max_length=64,
        unique=True,
        verbose_name='Идентификатор',
        help_text=('Идентификатор страницы для URL;'
                   ' разрешены символы латиницы,'
                   ' цифры, дефис и подчёркивание.')
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(PublishedModel):
    name = models.CharField(
        max_length=256,
        verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class PostQuerySet(models.QuerySet):

    def published(self):
        return self.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )

    def with_relations(self):
        return self.select_related(
            'author',
            'location',
            'category'
        )

    def ordered(self):
        return self.order_by('-pub_date')

    def with_comments(self):
        return self.annotate(
            comment_count=models.Count('comments')
        )

    def from_author(self, user):
        return self.filter(author=user)


class Post(PublishedModel):
    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок'
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата и время публикации',
        help_text=('Если установить дату'
                   ' и время в будущем'
                   ' — можно делать '
                   'отложенные публикации.')
    )
    image = models.ImageField(
        verbose_name='Фото',
        blank=True,
        upload_to='blog_images'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Категория'
    )
    objects = models.Manager()
    post_set = PostQuerySet.as_manager()

    @staticmethod
    def get_page_obj(request, queryset):
        paginator = Paginator(queryset, 10)
        page_number = request.GET.get('page')
        return paginator.get_page(page_number)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField(verbose_name='Текст')
    created_at = models.DateTimeField(
        auto_now=False,
        auto_now_add=True,
        verbose_name='Добавлено'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)
