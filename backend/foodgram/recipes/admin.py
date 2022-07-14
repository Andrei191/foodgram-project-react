from django.contrib import admin

from .models import (
    Favorite,
    Ingridient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    ShoppingCart,
    Tag,
)


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag
    extra = 1


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeTagInline, RecipeIngredientInline)
    list_display = ("name", "author", "favorite_recipe")
    list_filter = (
        "name",
        "author",
        "tags",
    )

    def favorite_recipe(self, obj):
        return obj.favorite_recipe.all().count()


class IngridientsAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    list_filter = ("name",)


class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = ("ingredient", "recipe", "amount")
    list_filter = (
        "ingredient",
        "recipe",
    )


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    list_filter = ("user", "recipe")


class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "slug")
    list_filter = ("name", "slug")


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    list_filter = ("user", "recipe")


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingridient, IngridientsAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientsAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
