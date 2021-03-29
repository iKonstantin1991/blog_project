from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        'Название группы',
        max_length=200,
        help_text='Напишите название группы'
    )
    slug = models.SlugField(
        'Слаг',
        unique=True,
        help_text='Укажите слаг'
    )
    description = models.TextField(
        'Описание',
        help_text='Добавьте описание группы'
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        'Текст',
        help_text='Напишите текст записи'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        help_text='Выберите группу'
    )
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        verbose_name='Комментируемый пост',
        on_delete=models.CASCADE,
        related_name='comments',
        help_text='Выберите пост'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        'Текст комментария',
        help_text='Напишите текст комментария'
    )
    created = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )

    class Meta:
        ordering = ['created']

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Пользователь на которого подписан',
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription')
        ]

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
