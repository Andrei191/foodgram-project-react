import django_filters
from recipes.models import Ingridient, Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name="tags__slug",
        to_field_name="slug",
    )
    is_favorited = django_filters.NumberFilter(
        method="get_is_favorited",
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        method="get_is_in_shopping_cart",
    )

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "author",
            "favorite_recipe",
            "recipe_in_shopping_cart",
        )

    def get_is_favorited(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            if value == 1:
                return queryset.filter(favorite_recipe__user=self.request.user)
            return queryset.exclude(favorite_recipe__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            if value == 1:
                return queryset.filter(
                    recipe_in_shopping_cart__user=self.request.user
                )
            return queryset.exclude(
                recipe_in_shopping_cart__user=self.request.user
            )
        return queryset


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
    )

    class Meta:
        fields = ("name",)
        model = Ingridient
