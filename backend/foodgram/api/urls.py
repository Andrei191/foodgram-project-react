from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (
    DownloadShoppingCartAPIView,
    FavoriteAPIView,
    IngredientsViewSet,
    RecipesViewSet,
    ShoppingCartAPIView,
    TagsViewSet,
)

router = SimpleRouter()

router.register("tags", TagsViewSet)
router.register("ingredients", IngredientsViewSet)
router.register("recipes", RecipesViewSet)


urlpatterns = [
    path(
        "recipes/<int:id>/favorite/",
        FavoriteAPIView.as_view(),
        name="favorite",
    ),
    path(
        "recipes/<int:id>/shopping_cart/",
        ShoppingCartAPIView.as_view(),
        name="shopping_cart",
    ),
    path(
        "recipes/download_shopping_cart/",
        DownloadShoppingCartAPIView.as_view(),
        name="download_shopping_cart",
    ),
    path("", include(router.urls)),
]
