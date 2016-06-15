from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

def get_now():
    return timezone.now()
# Create your models here.

class Mturker(models.Model):
    user = models.OneToOneField(User)
    treatment = models.CharField(max_length=256, null=True)
    verified = models.IntegerField(default=0)
    accepted = models.IntegerField(null=True)
    start = models.DateTimeField(null=True, blank=True)
    def gen_keycode(self):
        if not self.keycode:
            self.keycode = str(uuid.uuid1())
            self.save()

class Image(models.Model):
    filename = models.CharField('Filename', max_length=512)
    batch = models.CharField(max_length=256)

    def get_url(self):
        return "http://bfidata.s3-website-us-east-1.amazonaws.com/libraryimages/{}".format(self.filename)

    def check_status(self,user):
        rs = user.task_set.filter(task_id=self.id)
        if rs.count() == 1:
            status = rs[0].finished
        else:
            status = 0
        return status

    def __str__(self):
        return self.filename

class WorkTimer(models.Model):
    user = models.ForeignKey(User)
    task = models.ForeignKey("Task", null=True)
    page = models.CharField(max_length=28, null=True)
    value = models.IntegerField()
    token = models.CharField(max_length=256)
    timestamp = models.DateTimeField(auto_now_add=True)

class Task(models.Model):

    user = models.ForeignKey(User)
    image = models.ForeignKey(Image)

    readable = models.IntegerField(null=True)
    text = models.TextField(null=True, blank=True)
    order = models.IntegerField(null=True)
    status = models.IntegerField(default=0)

    timestarted = models.DateTimeField(default=get_now)
    timefinished = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.finished == 1 and self.timefinished == None:
            self.timefinished = get_now()
        super(Task, self).save(*args, **kwargs)

    def __str__(self):
        if self.street_num and self.street_nam:
            y = "{}".format(self.year) if self.year else ""
            m = self.month if self.month else ""
            return "{} {} {}-{}".format(self.street_num, self.street_nam, m, y)
        else:
            return self.image.filename


def get_now():
    return timezone.now()

class EventLog(models.Model):
    user = models.ForeignKey(User)
    task = models.ForeignKey(Task, null=True)
    name = models.CharField(max_length=256)
    description = models.CharField(max_length=512, blank=True)
    timestamp = models.DateTimeField(default=get_now)



