from django.conf.urls import url

from . import views, views_info, views_search, views_group


urlpatterns = [
    # views
    url(r'^$', views.IndexView, name='index'),
    url(r'^settings/$', views.ProfileSettingsView, name='settings'),
    url(r'^profile/(?P<user>\w+)$', views.ProfileView, name='profile'),
    url(r'^login/$', views.LoginView, name='login'),
    url(r'^login/pleaseVerify', views.PleaseVerifyView, name='pleaseVerify'),
    url(r'^verify/(?P<user>\w\S+)/(?P<hash>\w\S+)$', views.Verify, name='verify'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^message/(?P<msg>[0-9]+)$', views.MessageView, name='message'),
    url(r'^notification/$', views.NotificationView, name='notification'),
    url(r'^more/$', views.load_more, name='more'),
    url(r'^update/$', views.update, name='update'),
    url(r'^404/$', views.vierNullVier, name='404'),

    # views_into
    url(r'^info/$', views_info.InfoView, name='info'),
    url(r'^info/faq/$', views_info.FAQView, name='faq'),
    url(r'^info/support/$', views_info.SupportView, name='support'),

    # views_search
    url(r'^hashtag/(?P<text>\w\S+)$', views_search.HashtagView, name='hashtag'),
    url(r'^search/$', views_search.SearchView, name='search'),

    # views_group
    url(r'^add/group$', views_group.GroupAddView, name='addgroup'),
    url(r'^group/(?P<groupshort>\w+)$', views_group.GroupView, name='group'),
    url(r'^group/(?P<groupshort>\w+)/settings$', views_group.GroupSettingsView, name='group_settings'),
    url(r'^group/(?P<groupshort>\w+)/djln$', views_group.djlgroup, name='djlgroup'),  # delete, join, leave
]
