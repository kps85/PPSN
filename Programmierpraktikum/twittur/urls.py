from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^info/$', views.info, name='info'),
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^login/$', views.login, name='login'),
]
