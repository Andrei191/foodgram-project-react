from django.http.response import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from recipes.models import Recipe
from rest_framework import status
from rest_framework.response import Response


def create_file(unique_ingredients):
    with open("Ingredients_list.txt", "w", encoding="utf-8") as file:
        for key in unique_ingredients:
            file.write(
                (
                    f'{key["recipe__ingredients__name"]} - {key["summa"]}'
                    f'{key["recipe__ingredients__measurement_unit"]} \n'
                )
            )


def get_ingredients_list_and_return_response(file_location):
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


def custom_post(self, request, id, custom_serializer, field):
    user_id = request.user.id
    data = {"user": user_id, field: id}
    serializer = custom_serializer(data=data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def custom_delete(self, request, id, model):
    user = request.user
    recipe = get_object_or_404(Recipe, id=id)
    deleting_obj = model.objects.all().filter(user=user, recipe=recipe)
    if not deleting_obj:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    deleting_obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
