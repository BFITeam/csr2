from .models import Image, Task, WorkTimer, EventLog
from django.shortcuts import render, redirect
from django.utils import timezone
import datetime
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

def check_for_spam(user_id, seconds):
    try:
        worktimer = WorkTimer.objects.filter(user_id=user_id).order_by('-timestamp')[0]
    except IndexError:
        return False

    if timezone.now() - worktimer.timestamp < datetime.timedelta(0,29) and int(seconds) == int(worktimer.value):
        return True
    else:
        return False

def check_verified(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.user.mturker.verified:
            return redirect('data:unauthorized', message=1)
        elif not request.user.mturker.check_access():
            return redirect('data:unauthorized', message=2)
        else:
            return view_func(request, *args, **kwargs)
    return _wrapped_view_func

def timeout_logging(view_func):
    def _wrapped_view_func(request, image_id=None, *args, **kwargs):
        if not request.user.is_authenticated():
            return render(request, 'login.html', {'message': "logged out due to inactivity"})
        if request.method == "POST":
            if image_id:
                task = Task.objects.get(user_id=request.user.id, image_id=image_id)
                eventlog = EventLog(user_id=request.user.id, task_id=task.id, name=request.POST['action'])
                if not check_for_spam(request.user.id, request.POST['seconds']):
                    worktimer, created = WorkTimer.objects.get_or_create(user_id=request.user.id, task_id=task.id, value=request.POST['seconds'], token=request.POST['token'], page="task")
            else:
                eventlog = EventLog(user_id=request.user.id, name=request.POST['action'])
            eventlog.save()
        if image_id:
            return view_func(request, image_id, *args, **kwargs)
        else:
            return view_func(request, *args, **kwargs)
    return _wrapped_view_func
