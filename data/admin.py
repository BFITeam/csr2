from django.contrib import admin
from .models import WorkTimer, Task, EventLog, Mturker, TreatmentCell
from django.contrib.auth.models import User
import user_patch
# Register your models here.

class TimeSheet(User):
    class Meta:
       proxy = True

@admin.register(WorkTimer)
class WorkTimerAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'token', 'value', 'timestamp',)
    readonly_fields = ('user','timestamp')
    search_fields = ['user__username']
    def get_username(self, i):
        return i.user.username

class HoursInline(admin.TabularInline):
    model = WorkTimer
    fields = ('value', 'token')
    readonly_fields = ('token',)
    extra = 0

@admin.register(TimeSheet)
class BillableHoursAdmin(admin.ModelAdmin):
    fields = ('username',)
    readonly_fields = ('username', 'billable_hours',)
    list_display = ('username', 'get_billable_hours')

    inlines = [
        HoursInline
    ]

    def billable_hours(self, x):
        return x.get_billable_hours()

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('user', 'image')
    readonly_fields = ('user', 'image',)
    search_fields = ['user__username']

@admin.register(Mturker)
class MturkerAdmin(admin.ModelAdmin):
    list_display = ('get_username','accepted', 'verified', 'get_hours', 'complete')
    def get_username(self, i):
        return i.user.username

    def get_hours(self, i):
        return i.get_hours()

    def complete(self, i):
        return i.check_finished()

@admin.register(EventLog)
class EventLogAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'name', 'user_id', 'timestamp',)

    def get_username(self, x):
        return x.user.username

@admin.register(TreatmentCell)
class TreatmentCellAdmin(admin.ModelAdmin):
    list_display = ('treatment', 'batch', 'blur', 'finished')

