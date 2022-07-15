from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class Tag(models.Model):
    name = models.CharField("Тег", max_length=200, unique=True)
    color = models.CharField("Цвет", max_length=200, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingridient(models.Model):
    name = models.CharField("Название", max_length=200)
    measurement_unit = models.CharField("Единица измерения", max_length=100)

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipe",
        verbose_name="автор",
    )
    tags = models.ManyToManyField(Tag, through="RecipeTag")
    name = models.CharField("Название", max_length=200)
    image = models.ImageField(
        upload_to="recipes/media/",
        verbose_name="Картинка",
    )
    ingredients = models.ManyToManyField(
        Ingridient, through="RecipeIngredient", verbose_name="ингредиент"
    )
    text = models.CharField("Описание", max_length=500)
    cooking_time = models.IntegerField()
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-pub_date"]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingridient,
        on_delete=models.PROTECT,
        related_name="ingredient",
        verbose_name="Ингредиент",
    )
    amount = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты в рецептах"


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe, related_name="recipe_tag", on_delete=models.CASCADE
    )
    tags = models.ForeignKey(
        Tag,
        related_name="recipe_tag",
        on_delete=models.DO_NOTHING,
        verbose_name="Тег",
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorite",
        verbose_name="пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorite_recipe",
        verbose_name="рецепт",
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["user", "recipe"], name="recipe_in_favorite_unique"
            )
        ]
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_in_shopping_cart",
        verbose_name="Рецепт",
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["user", "recipe"], name="recipe_in_shopping_cart"
            )
        ]
        verbose_name = "Список покупок"
        verbose_name_plural = "Список покупок"
