from django.conf.urls import url
from django.contrib.auth.views import login, logout


from . import views, views_info

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^info/$', views_info.info, name='info'),
    url(r'^info/faq/$', views_info.faq, name='faq'),
    url(r'^info/support/$', views_info.support, name='support'),
    url(r'^hashtag/(?P<text>\w+)$', views.hashtag, name='hashtag'),
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^profile/(?P<user>\w+)$', views.profile, name='profile'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^search/$', views.search, name='search'),
]

