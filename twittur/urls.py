from django.conf.urls import url

from . import views, views_info, views_search, views_group


urlpatterns = [
    # views
    url(r'^$', views.index, name='index'),
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^profile/(?P<user>\w+)$', views.profile, name='profile'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),

    # views_into
    url(r'^info/$', views_info.info, name='info'),
    url(r'^info/faq/$', views_info.faq, name='faq'),
    url(r'^info/support/$', views_info.support, name='support'),

    # views_search
    url(r'^hashtag/(?P<text>\w\S+)$', views_search.hashtag, name='hashtag'),
    url(r'^search/$', views_search.search, name='search'),

    # views_group
    url(r'^addgroup/$', views_group.addgroup, name='addgroup'),
    url(r'^group/(?P<groupshort>\w\S+)$', views_group.group, name='group'),
    url(r'^group/(?P<groupshort>\w+)/login$', views_group.logingroup, name='logingroup'),

]
