from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import random

class Constants:
    endogBatchNumber = 10
    endogBatchLength = 5
    number_of_subjects = 60
    charity = "UNICEF"
    charity_url = "https://www.unicefusa.org/"
    treatments = {
        'T0_NoSort':{
            'sorting': False,
            'wage': '12',
            'wagebill': '0',
            },
        'TN_CSR_High_Sort':{
            'sorting': True,
            'wage': '12',
            'wagebill': '10',
            },
        'TN_CSR_High_NoSort':{
            'sorting': False,
            'wage': '12',
            'wagebill': '10'
            },
        'TM-Wage_Low_Sort':{
            'sorting': True,
            'wage': '10.80',
            'wagebill': '1.20',
            },
    }

def get_now():
    return timezone.now()
# Create your models here.

class Mturker(models.Model):
    user = models.OneToOneField(User)
    verified = models.IntegerField(default=0)
    accepted = models.IntegerField(null=True, blank=True)
    start = models.DateTimeField(default=get_now)
    mturkid = models.CharField(max_length=256, null=True, blank=True)
    assignmentId = models.CharField(max_length=256, null=True, blank=True)
    batch = models.CharField(max_length=128, null=True, blank=True)
    treatmentcell = models.ForeignKey('TreatmentCell', null=True)
    instructionsCount = models.IntegerField(default=0)

    upfront_payment = models.CharField(max_length=128, default=0)
    upfront_payment_bool = models.BooleanField(default=False)
    end_payment = models.CharField(max_length=128, default=0)
    end_payment_bool = models.BooleanField(default=False)

    batchOrder = models.CharField(max_length=64, null=True)
    imageRound = models.IntegerField(default=0)

    finished = models.BooleanField(default=False)

    def get_payment_values(self):
        tc = self.treatmentcell
        if tc.treatment != "endog":
            if tc.upfront == 0:
                upfront = 0
                self.upfront_payment_bool = 1
                self.end_payment = tc.wage
            else:
                upfront = float(tc.upfront)/100 * float(tc.wage)
                self.end_payment = "%.2f" % ((100 - float(tc.upfront))/100 * float(tc.wage))
            self.upfront_payment = "%.2f" % upfront
            self.save()

    def check_for_endog_payments(self):
        tc = self.treatmentcell
        if tc.treatment == "endog":
            quantityWorked = int(len(self.user.task_set.filter(status=1)))/Constants.endogBatchLength * float(tc.wage)
            if float(quantityWorked) > float(self.end_payment):
                self.end_payment = "%.2f" % (float(self.end_payment) + float(tc.wage))
                self.save()
                return True
            else:
                return False
        else:
            return False

    def get_number_of_images(self):
        images = Image.objects.filter(treatment=self.mturker.treatmentcell.imageLimit).filter(batchNo=0)
        return len(images)

    def assign_treatmentcell(self, tcId, mturkid, assignmentId):
        if not self.treatmentcell:
            tc = TreatmentCell.objects.get(id=tcId)
            if tc.imageLimit == "endog":
                string = ''
                for x in range(Constants.endogBatchNumber):
                    string += str(x)
            else:
                string = '0'
            self.batchOrder = string
            self.treatmentcell_id = tcId
            self.verified = 1
            self.mturkid = mturkid
            self.assignmentId = assignmentId
            self.save()

    def increment_counter(self):
        self.instructionsCount += 1
        self.save()

    def check_finished(self):
        try:
            if len(self.user.task_set.filter(status=1)) == len(Image.objects.filter(treatment=self.treatmentcell.imageLimit)) or self.finished == True:
                self.finished = True
                self.save()
                return True
            else:
                return False
        except AttributeError:
            return False

    def get_batchNo(self):
        tasks = self.user.task_set.filter(status=1)
        if self.treatmentcell.imageLimit == "exog":
            batchNo = 0
        else:
            try:
                batchNo = int(self.batchOrder[self.imageRound])
            except IndexError:
                batchNo = False
        return batchNo

    def check_for_pause(self):
        if self.treatmentcell == "endog":
            images = Images.objects.filter(treatment="endog")
            tasks = self.user.task_set.filter(status=1)
            if len(tasks) > 0 and len(tasks) % len(images) == 0:
                return True
            else:
                return False
        else:
            return False

    def get_task(self):
        current = False
        batchNo = self.get_batchNo()
        if not batchNo:
            return False, False, False, False
        tasks = self.user.task_set.all()
        progress = len(tasks.filter(image__batchNo=batchNo))
        images = Image.objects.filter(treatment=self.treatmentcell.imageLimit).filter(batchNo=batchNo).order_by('?')
        unfinished = tasks.filter(status=0)
        finished = tasks.filter(status=1)
        remaining = len(images)-len(finished)
        print "Number of remaining tasks:", remaining
        print "Number of unfinished tasks:",len(unfinished)
        if len(unfinished) > 0:
            current = unfinished[0]
        if len(unfinished) == 0:
            for x in range(len(images)):
                tempImage = images[x]
                current, created = Task.objects.get_or_create(user_id=self.user.id, image_id=tempImage.id)
                if created == True:
                    break
                else:
                    current = False
        if not current:
            entry = False
        else:
            entry = "text" if current.readable else "readable"
        if current == False:
            try:
                self.treatmentcell.finished = 1
                self.treatmentcell.save()
            except AttributeError:
                pass
        return current, entry, len(tasks), progress

    def get_hours(self):
        worktimers = self.user.worktimer_set.all()
        return sum([x.value for x in worktimers])

class Image(models.Model):
    filename = models.CharField('Filename', max_length=512, null=True)
    treatment = models.CharField('Exog or Endog?', max_length=128, null=True)
    batchNo = models.IntegerField(null=True, blank=True)

    def get_url(self):
        return "http://bfidata.s3-website-us-east-1.amazonaws.com/libraryimages/{}.jpg".format(self.filename)

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

class TreatmentCell(models.Model):
    treatment = models.CharField(max_length=256, null=True)
    imageLimit = models.CharField(max_length=256, null=True)
    finished = models.BooleanField(default=False)
    batch = models.CharField(max_length=128)
    upfront = models.IntegerField(default=0)
    sorting = models.NullBooleanField()
    wage = models.CharField(max_length=128, null=True)
    wagebill = models.CharField(max_length=128, null=True)
    csr = models.NullBooleanField()

    def get_remaining(self):
        return 100 - self.upfront

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.treatment


