from django.shortcuts import render, render_to_response, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect, HttpResponse
from .models import Image, Task, EventLog, WorkTimer, Mturker
from django.forms.models import inlineformset_factory, modelform_factory
from .decorators import check_verified
from forms import MenuItemForm
from django.db import models
from django import forms
from django.conf import settings
import user_patch
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User
import uuid
# Create your views here.

@login_required(login_url="/login/")
def index(request):
    mturker, create = Mturker.objects.get_or_create(user_id=request.user.id)

    return HttpResponseRedirect(reverse('data:info'))

@login_required(login_url="/login/")
@check_verified
def info(request):
    mturker, create = Mturker.objects.get_or_create(user_id=request.user.id)
    MturkerForm = modelform_factory(Mturker, fields=['accepted',])
    if request.user.mturker.accepted == 1:
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
        'description': "You are going to work on something",
        'mturkerform': mturkerform,
    }
    return render(request, 'data/description.html', context)


@login_required(login_url='/login/')
@check_verified
def begin(request):
    return render(request, 'data/main.html')

@login_required(login_url='/login/')
@check_verified
def task_entry(request):
    task, entry, completed = request.user.mturker.get_task()
    if not task:
        return redirect('data:complete')
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
    return render(request, 'data/complete.html')



@login_required(login_url="/login/")
def list_images(request):
    try:
        referer = request.META["HTTP_REFERER"]
    except KeyError:
        referer = "DNE"
    if "/login/" in referer:
        clickmodal = "yes"
    else:
        clickmodal = None
    images = request.user.get_tasks()
    context = {
        'images': images,
        'clickmodal': clickmodal,
    }
    return render(request, "data/images.html", context)


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
    worktimer, created = WorkTimer.objects.get_or_create(user_id=request.user.id, page="home", value=int(time), token=token)
    response = HttpResponse()
    return response

def unauthorized(request):
    return render(request, 'data/unauthorized.html')

def keygen(request):
    created = False
    while not created:

        user = User(username=str(uuid.uuid1())[:30])
        user.set_password("none")
        try:
            user.save()
        except IntegrityError:
            continue
        else:
            created = True
    context = {'user': user}
    return render(request, "data/keygen.html", context)
