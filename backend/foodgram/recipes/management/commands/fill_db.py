import json

from django.core.management.base import BaseCommand
from recipes.models import Ingridient


class Command(BaseCommand):
    def handle(self, *args, **options):

        with open("./ingredients.json", "rb") as f:
            data = json.load(f)

            for val in data:
                ingridient = Ingridient()
                ingridient.name = val["name"]
                ingridient.measurement_unit = val["measurement_unit"]
                ingridient.save()
        print("finished")
