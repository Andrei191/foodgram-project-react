from django.urls import include, path
from djoser import views
from rest_framework.routers import SimpleRouter

from .views import (  # isort:skip
    DownloadShoppingCartAPIView,  # isort:skip
    FavoriteAPIView,  # isort:skip
    FollowCreateAPIView,  # isort:skip
    FollowListAPIView,  # isort:skip
    IngredientsViewSet,  # isort:skip
    RecipesViewSet,  # isort:skip
    ShoppingCartAPIView,  # isort:skip
    TagsViewSet,  # isort:skip
)  # isort:skip

# isort:skip
urlpatterns = []

router = SimpleRouter()

router.register("tags", TagsViewSet)
router.register("ingredients", IngredientsViewSet)
router.register("recipes", RecipesViewSet)


urlpatterns = [
    path(
        "users/<int:id>/subscribe/",
        FollowCreateAPIView.as_view(),
        name="subscribe",
    ),
    path(
        "users/subscriptions/",
        FollowListAPIView.as_view(),
        name="subscriptions",
    ),
    path("auth/token/login/", views.TokenCreateView.as_view(), name="login"),
    path(
        "auth/token/logout/", views.TokenDestroyView.as_view(), name="logout"
    ),
    path("", include("djoser.urls")),
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
