from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import UniqueConstraint


class User(AbstractUser):
    username = models.TextField(
        "логин",
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[-a-zA-Z0-9_]+$", message="Недопустимое имя"
            )
        ],
    )
    email = models.EmailField("email адрес", unique=True, max_length=254)
    first_name = models.TextField("Имя", max_length=150)
    last_name = models.TextField("Фамилия", max_length=150)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    following = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Подписка",
    )

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            UniqueConstraint(
                fields=["user", "following"], name="follow_unique"
            )
        ]
