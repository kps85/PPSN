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
    url(r'^login/$', views.login_view, name='login'),
    url(r'^login/pleaseVerify', views.please_verify_view, name='pleaseVerify'),
    url(r'^settings/$', views.profile_settings_view, name='settings'),
    url(r'^profile/(?P<user>\w+)$', views.profile_view, name='profile'),
    url(r'^message/(?P<msg>[0-9]+)$', views.message_view, name='message'),
    url(r'^notification/$', views.notification_view, name='notification'),

    # views_info
    url(r'^info/$', views_info.info_view, name='info'),
    url(r'^info/faq/$', views_info.faq_view, name='faq'),
    url(r'^info/support/$', views_info.support_view, name='support'),

    # views_search
    url(r'^hashtag/(?P<text>[a-zA-Z0-9-_()+-/=]+|\w+)$', views_search.hashtag_view, name='hashtag'),
    url(r'^search/$', views_search.search_view, name='search'),

    # views_group
    url(r'^add/group$', views_group.group_add_view, name='addgroup'),
    url(r'^group/(?P<groupshort>\w+)$', views_group.group_view, name='group'),
    url(r'^group/(?P<groupshort>\w+)/settings$', views_group.group_settings_view, name='group_settings'),
    url(r'^group/(?P<groupshort>\w+)/djln$', views_group.djlgroup, name='djlgroup'),  # delete, join, leave

    # function_urls
    url(r'^get_notification/$', csrf_exempt(functions.get_notification), name='get_notification'),
    url(r'^logout/$', functions.logout, name='logout'),
    url(r'^more/$', functions.load_more, name='more'),
    url(r'^update/$', functions.update, name='update'),
    url(r'^verify/(?P<user>\w\S+)/(?P<hash_item>\w\S+)$', functions.verify, name='verify'),

    # api_urls
    url(r'^api/set/(?P<user>\w+)/(?P<hash_item>\w+)$', csrf_exempt(views_api.message_set), name='message_set'),
    url(r'^api/get$', csrf_exempt(views_api.message_get), name='message_get'),

    # error_urls
    url(r'^noscript/$', views.no_script, name='no_script'),
    url(r'^404/$', views.vier_null_vier, name='404'),
    url(r'^\w+', views.vier_null_vier, name='404'),
]
