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
            next(csvReader, None)
            for row in csvReader:
                if row[4] == "NoSort":
                    sorting = False
                else:
                    sorting = True
                wage = str(row[5]).replace("$",'')
                tc = TreatmentCell(treatment=row[1], upfront=row[2], imageLimit=row[3], sorting=sorting, wage=wage, csr=row[6], batch=row[7])
                tc.save()


