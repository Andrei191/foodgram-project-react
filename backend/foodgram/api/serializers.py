from django.db.models import F
from django.forms import ValidationError
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.models import Follow, User  # isort:skip
from recipes.models import (  # isort:skip
    Favorite,  # isort:skip
    Ingridient,  # isort:skip
    Recipe,  # isort:skip
    RecipeIngredient,  # isort:skip
    ShoppingCart,  # isort:skip
    Tag,  # isort:skip
)  # isort:skip


class CustomUserSerializer(UserSerializer):

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User  # new
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request.user.is_anonymous:
            return False
        user = request.user
        following = obj.follower.filter(user=obj, following=user)
        return following.exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """регистрация нового пользователя"""

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "username",
            "first_name",
            "last_name",
        )


class FollowCreateSerializer(serializers.ModelSerializer):
    """подписка на пользователя и отписка от него"""

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    following = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Follow
        fields = (
            "user",
            "following",
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=("user", "following"),
                message="Вы уже подписаны на этого пользователя",
            )
        ]

    def validate_following(self, value):
        user = self.context.get("request").user
        if user == value:
            raise serializers.ValidationError(
                "Вы не можете подписаться на самого себя!"
            )
        return value


class FollowRecipeSerializers(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class FollowListSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source="recipes.count", read_only=True
    )

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "recipes",
            "is_subscribed",
            "recipes_count",
        )
        read_only_fields = fields

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request.user.is_anonymous:
            return False
        user = request.user
        following = obj.follower.filter(user=obj, following=user)
        return following.exists()

    def get_recipes(self, obj):
        request = self.context.get("request")
        context = {"request": request}
        recipes = obj.recipes.all()
        return FollowRecipeSerializers(
            recipes, context=context, many=True
        ).data


class TagListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )


class IngridientsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingridient
        fields = ("id", "name", "measurement_unit")


class ShowRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class RecipeListSerializer(serializers.ModelSerializer):

    tags = TagListSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return ShowRecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context["request"]
        if request.user.is_anonymous:
            return False
        user_id = request.user.id
        favorite = Favorite.objects.all().filter(user=user_id, recipe=obj)
        return favorite.exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context["request"]
        if request.user.is_anonymous:
            return False
        user_id = request.user.id
        recipe_in_cart = ShoppingCart.objects.all().filter(
            user=user_id, recipe=obj
        )
        return recipe_in_cart.exists()


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingridient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "amount",
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = RecipeIngredientSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def add_recipe_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            ingredient_id = ingredient["id"]
            amount = ingredient["amount"]
            RecipeIngredient.objects.update_or_create(
                recipe=recipe,
                ingredient=ingredient_id,
                defaults={"amount": amount},
            )

    def create(self, validated_data):
        author = self.context.get("request").user
        tag_from_data = validated_data.pop("tags")
        ingredients_from_data = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.add_recipe_ingredients(ingredients_from_data, recipe)
        recipe.tags.set(tag_from_data)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.text = validated_data.get("text", instance.text)
        instance.image = validated_data.get("image", instance.image)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )
        tag_from_data = validated_data.pop("tags")
        if tag_from_data:
            instance.tags.set(tag_from_data)

        ingredients_from_data = self.validated_data.pop("ingredients")
        instance.ingredients.clear()
        self.add_recipe_ingredients(ingredients_from_data, instance)
        instance.save()
        return instance

    def validate(self, data):
        ingredients = self.initial_data.get("ingredients")
        if ingredients == []:
            raise ValidationError(
                {"Ошибка": "Необходимо выбрать хотя бы один ингредиент"}
            )
        amounts = data.get("ingredients")
        if [item for item in amounts if item["amount"] < 1]:
            raise serializers.ValidationError(
                {"amount": "Минимальное количество ингридиента 1"}
            )
        for ingredient in ingredients:
            if ingredients.count(ingredient) > 1:
                id = ingredient["id"]
                name = Ingridient.objects.all().get(id=id).name
                raise ValidationError({f"{name}": f"{name} уже есть в списке"})
        return data

    def to_representation(self, recipe):
        return RecipeListSerializer(
            recipe, context={"request": self.context.get("request")}
        ).data


class ShowRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Favorite
        fields = ("user", "recipe")

    def validate_recipe(self, data):
        user = self.context.get("request").user
        new_recipe = self.initial_data.get("recipe")
        if (
            Favorite.objects.all()
            .filter(user=user, recipe=new_recipe)
            .exists()
        ):
            raise ValidationError("Этот рецепт у вас уже в избранном")
        return data

    def to_representation(self, instance):
        return ShowRecipeSerializer(instance.recipe).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = ShoppingCart
        fields = ("user", "recipe")

    def validate_recipe(self, data):
        user = self.context.get("request").user
        recipe = self.initial_data.get("recipe")
        if (
            ShoppingCart.objects.all()
            .filter(user=user, recipe=recipe)
            .exists()
        ):
            raise ValidationError("Этот рецепт уже в вашей корзине")
        return data

    def to_representation(self, instance):
        return ShowRecipeSerializer(instance.recipe).data
