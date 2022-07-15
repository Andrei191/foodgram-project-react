from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status, views, viewsets
from rest_framework.response import Response

from .permissions import AuthorOrAdminOnly, ReadOnly
from .serializers import (
    FavoriteSerializer,
    FollowCreateSerializer,
    FollowListSerializer,
    IngridientsListSerializer,
    RecipeCreateSerializer,
    RecipeListSerializer,
    ShoppingCartSerializer,
    TagListSerializer,
)
from .utils import (
    create_file,
    custom_delete,
    custom_post,
    get_ingredients_list_and_return_response,
)

from recipes.models import (  # isort:skip
    Favorite,  # isort:skip
    Ingridient,  # isort:skip
    Recipe,  # isort:skip
    ShoppingCart,  # isort:skip
    Tag,  # isort: skip
)  # isort:skip
from users.models import Follow  # isort:skip

User = get_user_model()


class FollowCreateAPIView(views.APIView):
    def post(self, request, id):
        return custom_post(self, request, id, FollowCreateSerializer)

    def delete(self, request, id):
        user = request.user
        following = get_object_or_404(User, id=id)
        deleting_obj = Follow.objects.all().filter(
            user=user, following=following
        )
        return custom_delete(deleting_obj)
        # if not deleting_obj:
        #     return Response(status=status.HTTP_400_BAD_REQUEST)
        # deleting_obj.delete()
        # return Response(status=status.HTTP_204_NO_CONTENT)


class FollowListAPIView(generics.ListAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowListSerializer

    def get_queryset(self):
        user = self.request.user
        return User.objects.all().filter(following__user=user)


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagListSerializer
    permission_classes = [
        ReadOnly,
    ]


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingridient.objects.all()
    serializer_class = IngridientsListSerializer
    permission_classes = [
        ReadOnly,
    ]
    filter_backends = [
        filters.SearchFilter,
    ]
    search_fields = ("^name",)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeListSerializer
    permission_classes = [
        AuthorOrAdminOnly,
    ]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("tags__name",)
    actions_list = ["POST", "PATCH"]

    def get_permissions(self):
        if self.action == "retrieve":
            return (ReadOnly(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method in self.actions_list:
            return RecipeCreateSerializer
        return RecipeListSerializer


class FavoriteAPIView(views.APIView):
    permission_classes = [AuthorOrAdminOnly]

    def post(self, request, id):
        return custom_post(self, request, id, FavoriteSerializer)

    def delete(self, request, id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)
        deleting_obj = Favorite.objects.all().filter(user=user, recipe=recipe)
        return custom_delete(deleting_obj)


class ShoppingCartAPIView(views.APIView):
    def post(self, request, id):
        return custom_post(self, request, id, ShoppingCartSerializer)

    def delete(self, request, id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)
        deleting_obj = ShoppingCart.objects.all().filter(
            user=user, recipe=recipe
        )
        return custom_delete(deleting_obj)


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
