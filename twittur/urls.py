"""
-*- coding: utf-8 -*-
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

from . import functions, views, views_info, views_search, views_group


urlpatterns = [
    # views_general
    url(r'^$', views.index_view, name='index'),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^settings/$', views.profile_settings_view, name='settings'),
    url(r'^profile/(?P<user>\w+)$', views.profile_view, name='profile'),
    url(r'^message/(?P<msg>[0-9]+)$', views.message_view, name='message'),
    url(r'^notification/$', views.notification_view, name='notification'),
    url(r'^404/$', views.vier_null_vier, name='404'),

    # views_info
    url(r'^info/$', views_info.info_view, name='info'),
    url(r'^info/faq/$', views_info.faq_view, name='faq'),
    url(r'^info/support/$', views_info.support_view, name='support'),

    # views_search
    url(r'^hashtag/(?P<text>\w\S+)$', views_search.hashtag_view, name='hashtag'),
    url(r'^search/$', views_search.search_view, name='search'),

    # views_group
    url(r'^add/group$', views_group.group_add_view, name='addgroup'),
    url(r'^group/(?P<groupshort>\w+)$', views_group.group_view, name='group'),
    url(r'^group/(?P<groupshort>\w+)/settings$', views_group.group_settings_view, name='group_settings'),
    url(r'^group/(?P<groupshort>\w+)/djln$', views_group.djlgroup, name='djlgroup'),  # delete, join, leave

    # function_urls
    url(r'^logout/$', functions.logout, name='logout'),
    url(r'^more/$', functions.load_more, name='more'),
    url(r'^update/$', functions.update, name='update'),
]
