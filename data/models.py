from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import random

class Constants:
    number_of_subjects = 60
    charity = "Unicef"

def get_now():
    return timezone.now()
# Create your models here.

class Mturker(models.Model):
    user = models.OneToOneField(User)
    wage = models.CharField(max_length=64, null=True, blank=True)
    wagebill = models.CharField(max_length=64, null=True, blank=True)
    sorting = models.NullBooleanField()
    verified = models.IntegerField(default=0)
    accepted = models.IntegerField(null=True, blank=True)
    start = models.DateTimeField(default=get_now)
    batch = models.CharField(max_length=256, null=True)

    def get_task(self):
        images = Image.objects.filter(batch=self.batch)
        tasks = self.user.task_set.all()
        unfinished = tasks.filter(status=0)
        finished = tasks.filter(status=1)
        remaining = len(images)-len(finished)
        print "Number of remaining tasks:", remaining
        print "Number of unfinished tasks:",len(unfinished)
        if len(unfinished) > 0:
            current = unfinished[0]
        if len(unfinished) == 0:
            for x in range(len(images)):
                tempImage = random.choice(images)
                current, created = Task.objects.get_or_create(user_id=self.user.id, image_id=tempImage.id)
                if created == True:
                    break
                else:
                    current = False
        if not current:
            entry = False
        else:
            entry = "text" if current.readable else "readable"
        return current, entry, len(tasks)



class Image(models.Model):
    filename = models.CharField('Filename', max_length=512)
    batch = models.CharField(max_length=256, null=True)

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
    page = models.CharField(max_length=128, null=True)
    value = models.IntegerField()
    token = models.CharField(max_length=256)
    timestamp = models.DateTimeField(auto_now_add=True)

class Task(models.Model):
    YESNO_CHOICES = (
        (1, 'Yes'),
        (0, 'No'),
    )
    user = models.ForeignKey(User)
    image = models.ForeignKey(Image)

    readable = models.IntegerField(null=True, choices=YESNO_CHOICES)
    text = models.TextField(null=True)
    order = models.IntegerField(null=True)
    status = models.IntegerField(default=0)

    timestarted = models.DateTimeField(default=get_now)
    timefinished = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.status == 1 and self.timefinished == None:
            self.timefinished = get_now()
        super(Task, self).save(*args, **kwargs)

def get_now():
    return timezone.now()

class EventLog(models.Model):
    user = models.ForeignKey(User)
    task = models.ForeignKey(Task, null=True)
    name = models.CharField(max_length=256)
    description = models.CharField(max_length=512, blank=True)
    timestamp = models.DateTimeField(default=get_now)



