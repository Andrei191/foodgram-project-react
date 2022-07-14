import json

from django.core.management.base import BaseCommand
from recipes.models import Ingridients


class Command(BaseCommand):
    def handle(self, *args, **options):

        with open("../data/ingredients.json", "rb") as f:
            data = json.load(f)

            for val in data:
                ingridient = Ingridients()
                ingridient.name = val["name"]
                ingridient.measurement_unit = val["measurement_unit"]
                ingridient.save()
        print("finished")
