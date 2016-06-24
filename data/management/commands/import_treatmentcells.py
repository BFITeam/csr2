from django.core.management.base import BaseCommand, CommandError
from data.models import TreatmentCell
from django.conf import settings
import csv, os

class Command(BaseCommand):
    help = "Imports the menulist.csv file to the database"

    def handle(self, *args, **options):
        filename = os.path.join(settings.BASE_DIR,'treatmentcells.csv')
        with open(filename) as f:
            csvReader = csv.reader(f)
            for row in csvReader:
                tc = TreatmentCell(blur=row[0], treatment=row[1], batch=row[2])
                tc.save()


