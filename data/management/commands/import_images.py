from django.core.management.base import BaseCommand, CommandError
from data.models import Image
from django.conf import settings
import csv, os

class Command(BaseCommand):
    help = "Imports the image.csv file to the database"

    def handle(self, *args, **options):
        filename = os.path.join(settings.BASE_DIR,'images.csv')
        with open(filename) as f:
            csvReader = csv.reader(f)
            next(csvReader, None)
            for row in csvReader:
                img, created = Image.objects.get_or_create(filename=row[0], treatment=row[2], batchNo=int(row[3])-1)
                img.save()

