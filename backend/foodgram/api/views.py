from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, views, viewsets
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .permissions import AuthorOrAdmin, ReadOnly

from .serializers import (  # isort:skip
    FavoriteSerializer,  # isort:skip
    FollowCreateSerializer,  # isort:skip
    FollowListSerializer,  # isort:skip
    IngridientsListSerializer,  # isort:skip
    RecipeCreateSerializer,  # isort:skip
    RecipeListSerializer,  # isort:skip
    ShoppingCartSerializer,  # isort:skip
    TagListSerializer,  # isort:skip
)  # isort:skip
from .utils import (  # isort:skip
    create_file,  # isort:skip
    custom_delete,  # isort:skip
    custom_post,  # isort:skip
    get_ingredients_list_and_return_response,  # isort:skip
)  # isort:skip

# isort:skip
from recipes.models import (  # isort:skip
    Favorite,  # isort:skip
    Ingridient,  # isort:skip
    Recipe,  # isort:skip
    ShoppingCart,  # isort:skip
    Tag,  # isort: skip
)  # isort:skip
from users.models import Follow, User  # isort:skip

# User = get_user_model()


class FollowCreateAPIView(views.APIView):
    def post(self, request, id):
        user_id = request.user.id
        data = {"user": user_id, "following": id}
        serializer = FollowCreateSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        following = get_object_or_404(User, id=id)
        deleting_obj = Follow.objects.all().filter(
            user=user, following=following
        )
        if not deleting_obj:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        deleting_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagListSerializer
    pagination_class = None
    permission_classes = [
        ReadOnly,
    ]


class FollowListAPIView(generics.ListAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowListSerializer

    def get_queryset(self):
        user = self.request.user
        new_queryset = User.objects.all().filter(following__user=user)
        return new_queryset


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingridient.objects.all()
    serializer_class = IngridientsListSerializer
    pagination_class = None
    permission_classes = [
        ReadOnly,
    ]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeListSerializer
    permission_classes = [
        AuthorOrAdmin,
    ]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    actions_list = ["POST", "PATCH"]
    lookup_field = "id"

    def get_permissions(self):
        if self.action == "retrieve":
            return (ReadOnly(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method in self.actions_list:
            return RecipeCreateSerializer
        return RecipeListSerializer


class FavoriteAPIView(views.APIView):
    permission_classes = [AuthorOrAdmin]

    def post(self, request, id):
        user_id = request.user.id
        data = {"user": user_id, "recipe": id}
        serializer = FavoriteSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)
        deleting_obj = Favorite.objects.all().filter(user=user, recipe=recipe)
        if not deleting_obj:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        deleting_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartAPIView(views.APIView):
    def post(self, request, id):
        return custom_post(self, request, id, ShoppingCartSerializer, "recipe")

    def delete(self, request, id):
        return custom_delete(self, request, id, ShoppingCart)


class DownloadShoppingCartAPIView(views.APIView):
    def get(self, request):
        ingridients = (
            ShoppingCart.objects.annotate(
                summa=Sum("recipe__ingredients__ingredient__amount"),
            )
            .values(
                "recipe__ingredients__name",
                "recipe__ingredients__measurement_unit",
                "summa",
            )
            .filter(
                user=request.user,
            )
        )
        unique_ingredients = {
            x["recipe__ingredients__name"]: x for x in ingridients
        }.values()

        create_file(unique_ingredients)
        file_location = "./Ingredients_list.txt"
        return get_ingredients_list_and_return_response(file_location)
