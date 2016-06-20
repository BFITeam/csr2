from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^keygen', views.keygen, name='keygen'),
    url(r'^info', views.info, name='info'),
    url(r'^begin/$', views.begin, name="begin"),
    url(r'^taskentry/', views.task_entry, name="task_entry"),
    url(r'^login/$', views.my_login, name='login'),
    url(r'^logout/$', views.my_logout, name='logout'),
    url(r'^home_timer/$', views.home_timer, name='home_timer'),
    url(r'^unauthorized/$', views.unauthorized, name="unauthorized"),
    url(r'^complete', views.complete, name="complete"),
   ]
