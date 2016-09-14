from django.shortcuts import render, render_to_response, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect, HttpResponse
from .models import Image, Task, EventLog, WorkTimer, Mturker, Constants
from django.forms.models import inlineformset_factory, modelform_factory
from .decorators import check_verified
from forms import MenuItemForm
from django.db import models
from django import forms
from django.conf import settings
import user_patch
from django.contrib.auth import views as auth_views, authenticate, login
from django.contrib.auth.models import User
import uuid
from boto.mturk.price import Price
from worker import mturk
# Create your views here.

@login_required(login_url="/login/")
def index(request):
    mturker, create = Mturker.objects.get_or_create(user_id=request.user.id)

    return HttpResponseRedirect(reverse('data:info'))

@login_required(login_url="/login/")
@check_verified
def info(request):
    mturker, create = Mturker.objects.get_or_create(user_id=request.user.id)
    mturker.get_payment_values()
    MturkerForm = modelform_factory(Mturker, fields=['accepted',])
    if mturker.accepted == 1:
        return HttpResponseRedirect(reverse('data:begin'))
    elif request.user.mturker.accepted == 0:
        return redirect('data:unauthorized')
    if request.method == 'POST':
        mturkerform = MturkerForm(request.POST, instance=mturker)
        if mturkerform.is_valid():
            mturker.accepted = int(request.POST['accepted'])
            mturker.save()
            return redirect('data:begin') if mturker.accepted else redirect('data:unauthorized')
    else:
        mturkerform = MturkerForm(instance=mturker)
    context = {
        'Constants': Constants,
        'mturkerform': mturkerform,
        'mturker': request.user.mturker,
        'treatment': request.user.mturker.treatmentcell,
    }
    return render(request, 'data/description.html', context)


@login_required(login_url='/login/')
@check_verified
def begin(request):
    mturker = request.user.mturker
    if mturker.upfront_payment_bool == 0:
        print "sending upfront bonus"
        #pay them using boto and update upfront_payment_bool
        price = Price(amount=float(request.user.mturker.upfront_payment), currency_code="USD")
        requester_message = "here is {}% of your total bonus.".format(mturker.treatmentcell.upfront)
        mturk.grant_bonus(request.user.mturker.mturkid, request.user.mturker.assignmentId, price, requester_message)
        mturker.upfront_payment_bool = 1
        mturker.save()
    context = {
        'Constants': Constants,
        'mturker': request.user.mturker,
        'treatment': request.user.mturker.treatmentcell,
        }
    return render(request, 'data/main.html', context)

@login_required(login_url='/login/')
@check_verified
def task_entry(request):
    task, entry, completed = request.user.mturker.get_task()
    if not task:
        if request.user.mturker.check_finished():
            return redirect('data:complete')
        else:
            return redirect('data:endog_check')
    TaskForm = modelform_factory(Task, fields=[entry])
    taskform = TaskForm(instance=task)
    if request.method == "POST":
        taskform = TaskForm(request.POST, instance=task)
        if taskform.is_valid():
            setattr(task, entry, request.POST[entry])
            if entry == "text":
                task.status = 1
            if entry == "readable" and int(request.POST['readable']) == 0:
                task.status = 1
            task.order = completed
            task.save()
            taskform = TaskForm(instance=task)
            context = {
                'completed': completed,
                'taskform': taskform,
                'task': task,
                }
            return redirect('data:task_entry')
        else:
            taskform = TaskForm(instance=task)
    context = {
        'taskform': taskform,
        'task': task,
        'completed': completed,
    }
    return render(request, 'data/task_entry.html', context)

@login_required(login_url='/login/')
def complete(request):
    mturker = request.user.mturker
    tc = request.user.mturker.treatmentcell
    if tc.treatment == "endog":
        mturker.end_payment_bool = True
        if mturker.check_for_endog_payments() == True:
            price = Price(float(tc.wage), currency_code="USD")
            requester_message = "Here is your bonus of ${} for finishing a batch of images".format(tc.wage)
            mturk.grant_bonus(mturker.mturkid, mturker.assignmentId, price, requester_message)
    elif tc.treatment == "baseline":
        requester_message = "Here is your bonus payment for finishing the transcription task.".format(tc.wage)
        price = Price(float(mturker.end_payment), currency_code="USD")
        if mturker.end_payment_bool == False:
            mturk.grant_bonus(mturker.mturkid, mturker.assignmentId, price, requester_message)
            mturker.end_payment_bool = True
    elif "upfront" in tc.treatment:
        requester_message = "Here is the remaining {}% of your total bonus for finishing the images".format(100-tc.upfront)
        price = Price(float(mturker.end_payment), currency_code="USD")
        if mturker.end_payment_bool == False:
            mturk.grant_bonus(mturker.mturkid, mturker.assignmentId, price, requester_message)
            mturker.end_payment_bool = True
    mturker.save()
    return render(request, 'data/complete.html')

@login_required(login_url='/login/')
def endog_check(request):
    context = {}
    if request.user.mturk.check_for_endog_payments() == True:
        price = Price(float(request.user.mturker.treatmentcell.wage), currency_code="USD")
        requester_message = "Here is a bonus of ${} for finishing a batch of images".format(request.user.mturker.treatmentcell.wage)
        mturk.grant_bonus(request.user.mturker.mturkid, request.user.mturker.assignmentId, price, requester_message)
    if request.method == "POST":
        keepgoing = int(request.POST['accepted'])
        if keepgoing == 1:
            roundNo = request.user.mturker.imageRound + 1
            request.user.mturker.imageRound = roundNo
            request.user.mturker.save()
        if keepgoing == 0:
            request.user.mturker.finished = 1
            request.user.mturker.save()
        return redirect('data:task_entry')
    return render(request, 'data/check.html', context)



def my_login(request, *args, **kwargs):
    kwargs = {'template_name': "login.html",}
    response = auth_views.login(request, **kwargs)
    if response.status_code == 302:
        user = User.objects.get(username=request.POST['username'])
        event = EventLog(user_id=user.id, name="login")
        event.save()
    return response

def my_logout(request, *args, **kwargs):
    description = request.GET.get('message', '')
    if not request.user.is_authenticated():
        return render(request, 'login.html', {'message': "logged out due to inactivity"})
    event = EventLog(user_id=request.user.id, name="logout", description=description)
    event.save()
    return auth_views.logout(request, next_page="/", extra_context={'message': 'logged out due to inactivity'})

@login_required(login_url="/login/")
def log_event(request, image_id):
    task = Task.objects.get(image_id=image_id, user_id=request.user.id)
    url = "/taskentry/{}".format(task_id)
    event = EventLog(task_id=task.id, name="timeout")
    event.save()
    return redirect(url)

@csrf_protect
def home_timer(request):
    time = round(float(request.POST['time']))
    token = request.POST['token']
    page = request.POST['page']
    taskId = request.POST['task']
    if taskId != '':
        worktimer, created = WorkTimer.objects.get_or_create(user_id=request.user.id, page=page, value=int(time), token=token, task_id=taskId)
    else:
        worktimer, created = WorkTimer.objects.get_or_create(user_id=request.user.id, page=page, value=int(time), token=token)
    response = HttpResponse()
    return response

@csrf_protect
def instructions_counter(request):
    user = User.objects.get(id=request.POST['uid'])
    user.mturker.increment_counter()
    response = HttpResponse()
    return response

def unauthorized(request, message=None):
    context = { 'message': message }
    if request.user.mturker.verified == 1 and request.user.mturker.accepted != 0:
        return redirect('data:info')
    else:
        return render(request, 'data/unauthorized.html', context)

def keygen(request):
    if request.user.is_authenticated():
        return redirect("data:index")
    created = False
    user = User.objects.create_user(username=str(uuid.uuid1())[:30],password='none')
    user = authenticate(username=user.username, password="none")
    login(request, user)
    context = {
        'user': user,
        'keygen': True,
    }

    return render(request, "data/keygen.html", context)
