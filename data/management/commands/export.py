from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from data.models import Task, WorkTimer, EventLog, Image
from django.conf import settings
import csv, os

class Command(BaseCommand):
    help = "Exports task and tracking data"

    def get_headers(self, model):
        headers = []
        if model._meta.object_name != "EventLog" and model._meta.object_name != "User" and model._meta.object_name != "Image":
            headers.append('user')
        if model._meta.object_name == "Task":
            headers.append('image')
        q = model.objects.values()[0]
        for key, value in  q.items():
            headers.append(key)
        return headers

    def write_csv(self, filename, model):
        with open(filename, 'w') as f:
            writer = csv.writer(f, csv.excel)
            headers = self.get_headers(model)
            writer.writerow(headers)
            for obj in model.objects.all():
                row = []
                for h in headers:
                    if h == "text":
                        try:
                            row.append(getattr(obj, h).encode('utf8', 'replace'))
                        except AttributeError:
                            row.append(" ")
                    else:
                        row.append(getattr(obj,h))
                writer.writerow(row)

    def handle(self, *args, **options):
        exportDir = os.path.join(settings.BASE_DIR, 'export')
        if not os.path.isdir(exportDir):
            os.mkdir(exportDir)

        taskFile = os.path.join(exportDir, 'task.csv')
        self.write_csv(taskFile, Task)

        eventFile = os.path.join(exportDir, 'eventlog.csv')
        self.write_csv(eventFile, EventLog)

        workFile = os.path.join(exportDir, 'worktimer.csv')
        self.write_csv(workFile, WorkTimer)

        userFile = os.path.join(exportDir, "user.csv")
        self.write_csv(userFile, User)

        #imageFile = os.path.join(exportDir, "image.csv")
        #self.write_csv(imageFile, Image)



