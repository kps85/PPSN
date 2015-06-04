from django.conf.urls import url
from django.contrib.auth.views import login, logout


from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^info/$', views.info, name='info'),
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^profile/(?P<user>\w+)$', views.profile, name='profile'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout' ),
    url(r'^search/$', views.search, name='search' ),
    url(r'^search/#(?P<text>\w+)$', views.searchhashtag, name='searchhashtag' ),




]

