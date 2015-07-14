# -*- coding: utf-8 -*-
"""
@package twittur
@author twittur-Team (Lilia B., Ming C., William C., Karl S., Thomas T., Steffen Z.)
URLs
- views_general     standard views containing index, login, settings, profile, message, notification and 404
- views_info        info views containing info page, FAQ and support forms
- views_search      search views containing search results and hashtag
- views_group       group view containing adding a group, editing a group and the group itself
- function_urls     simple interface to return further information
"""


from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from . import functions, views, views_api, views_info, views_search, views_group


urlpatterns = [
    # views_general
    url(r'^$', views.index_view, name='index'),
    url(r'^(?i)install/$', views_api.install_view, name='install'),
    url(r'^(?i)login/$', views.login_view, name='login'),
    url(r'^(?i)login/pleaseVerify/', views.please_verify_view, name='pleaseVerify'),
    url(r'^(?i)settings/$', views.profile_settings_view, name='settings'),
    url(r'^(?i)profile/(?P<user>[a-zA-Z0-9-_.]+|\w+)/$', views.profile_view, name='profile'),
    url(r'^(?i)message/(?P<msg>[0-9]+)/$', views.message_view, name='message'),
    url(r'^(?i)notification/$', views.notification_view, name='notification'),

    # views_info
    url(r'^(?i)info/$', views_info.info_view, name='info'),
    url(r'^(?i)info/faq/$', views_info.faq_view, name='faq'),
    url(r'^(?i)info/support/$', views_info.support_view, name='support'),

    # views_search
    url(r'^(?i)hashtag/(?P<text>[a-zA-Z0-9-_.()+-=!?*]+|\w+)/$', views_search.hashtag_view, name='hashtag'),
    url(r'^(?i)search/$', views_search.search_view, name='search'),

    # views_group
    url(r'^(?i)add/group/$', views_group.group_add_view, name='addgroup'),
    url(r'^(?i)group/(?P<groupshort>[a-zA-Z0-9-_.]+|\w+)/$', views_group.group_view, name='group'),
    url(r'^(?i)group/(?P<groupshort>[a-zA-Z0-9-_.]+|\w+)/settings/$',
        views_group.group_settings_view, name='group_settings'),
    url(r'^(?i)group/(?P<groupshort>[a-zA-Z0-9-_.]+|\w+)/djln/$',
        views_group.djlgroup, name='djlgroup'),  # delete, join, leave

    # function_urls
    url(r'^(?i)get_notification/$', csrf_exempt(functions.get_notification), name='get_notification'),
    url(r'^(?i)logout/$', functions.logout, name='logout'),
    url(r'^(?i)more/$', functions.load_more, name='more'),
    url(r'^(?i)update/$', functions.update, name='update'),
    url(r'^(?i)favorite/(?P<msg>[0-9]+)/$', functions.favorite, name='favorite'),
    url(r'^(?i)verify/(?P<user>[a-zA-Z0-9-_.]+|\w\S+)/(?P<hash_item>\w\S+)/$', functions.verify, name='verify'),
    url(r'^(?i)refresh_hash/$', functions.refresh_hash, name='refresh_hash'),
    url(r'^(?i)reset_pw/(?P<user>[a-zA-Z0-9-_.]+|\w\S+)/(?P<hash_item>\w\S+)/$', functions.reset_pw, name='reset_pw'),

    # api_urls
    url(r'^(?i)api/set/(?P<user>[a-zA-Z0-9-_.]+|\w+)/(?P<hash_item>\w\S+)/$',
        csrf_exempt(views_api.message_set), name='message_set'),
    url(r'^(?i)api/get/$', csrf_exempt(views_api.message_get), name='message_get'),

    # error_urls
    url(r'^(?i)noscript/$', views.no_script, name='no_script'),
    url(r'^(?i)404/$', views.vier_null_vier, name='404'),
    url(r'^(?i)\w+', views.vier_null_vier, name='404'),
]
