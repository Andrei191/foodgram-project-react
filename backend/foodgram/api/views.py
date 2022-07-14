from django.contrib.auth import get_user_model
from django.http.response import HttpResponse, HttpResponseNotFound
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

from recipes.models import (  # isort:skip
    Favorite,  # isort:skip
    Ingridient,  # isort:skip
    Recipe,  # isort:skip
    ShoppingCart,  # isort:skip
    Tag,  # isort:skip
)  # isort:skip
from users.models import Follow  # isort:skip

User = get_user_model()


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
        user_id = request.user.id
        data = {"user": user_id, "recipes": id}
        serializer = FavoriteSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)
        deleting_obj = Favorite.objects.all().filter(user=user, recipes=recipe)
        if not deleting_obj:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        deleting_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartAPIView(views.APIView):
    def post(self, request, id):
        user_id = request.user.id
        data = {"user": user_id, "recipe": id}
        serializer = ShoppingCartSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)
        deleting_obj = ShoppingCart.objects.all().filter(
            user=user, recipe=recipe
        )
        if not deleting_obj:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        deleting_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingCartAPIView(views.APIView):
    def get(self, request):
        ingridients = {}
        user = request.user
        recipes_in_cart = ShoppingCart.objects.all().filter(user=user)

        for obj in recipes_in_cart:
            recipe = obj.recipe.recipe
            for val in recipe.all():
                name = val.ingredient.name
                amount = val.amount
                measurement_unit = val.ingredient.measurement_unit
                if name not in ingridients:
                    ingridients[name] = {
                        "measurement_unit": measurement_unit,
                        "amount": amount,
                    }
                else:
                    ingridients[name]["amount"] += amount

        with open("Ingredients_list.txt", "w", encoding="utf-8") as file:
            for key in ingridients:
                file.write(
                    (
                        f'{key} - {ingridients[key]["amount"]}'
                        f'{ingridients[key]["measurement_unit"]} \n'
                    )
                )

        file_location = "./Ingredients_list.txt"
        try:
            with open(file_location, "r", encoding="utf-8") as f:
                file_data = f.read()

            response = HttpResponse(file_data, content_type="text/plain")
            response[
                "Content-Disposition"
            ] = 'attachment; filename="Ingredients_list.txt"'
        except IOError:
            response = HttpResponseNotFound("<h1>File not exist</h1>")
        return response
