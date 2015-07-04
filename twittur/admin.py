"""
-*- coding: utf-8 -*-
@package twittur
@author twittur-Team (Lilia B., Ming C., William C., Karl S., Thomas T., Steffen Z.)
Admin Interface
- UserProfileAdmin: overview for userprofiles
- GroupAdmin:       overview for groups
- MsgAdmin:         overview for messages
- NTFCAdmin:        overview for notifications
- FAQAdmin:         overview for frequently asked questions
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import FAQ, GroupProfile, Hashtag, Message, Notification, UserProfile


# initialize admin view for UserProfiles
class UserProfileAdmin(admin.ModelAdmin):
    """
    fieldsets for single userprofile view
    - groups different fields and puts them in order
    sets attributes to be displayed in overview, sets links and puts them in order
    """
    # single-view
    fieldsets = [
        ('User',    {'fields': ['userprofile']}),
        ('Info',    {'fields': ['picture', 'academicDiscipline', 'studentNumber', 'location', 'safety']}),
        ('Other',   {'fields': ['ignoreM', 'ignoreU', 'ignore']}),
    ]
    # overview
    list_display = ('studentNumber', 'userprofile', 'academicDiscipline')
    list_display_links = ('studentNumber', 'userprofile')
    ordering = ('academicDiscipline', 'studentNumber', 'userprofile')


# initialize admin view for Groups
class GroupAdmin(admin.ModelAdmin):
    """
    fieldsets for single group view
    - groups different fields and puts them in order
    sets attributes to be displayed in overview, sets links and puts them in order
    """
    # single-view
    fieldsets = [
        ('SuperGroup',  {'fields': ['supergroup']}),
        ('Info',        {'fields': ['name', 'short', 'desc', 'password', 'picture', 'date', 'member', 'joinable']}),
        ('Admin',       {'fields': ['admin']}),
    ]
    # overview
    list_display = ('name', 'supergroup', 'admin')
    list_display_links = ('supergroup', 'name')
    ordering = ('-supergroup', 'name')


# initialize admin view for Messages
class MsgAdmin(admin.ModelAdmin):
    """
    fieldsets for single message view
    - groups different fields and puts them in order
    sets attributes to be displayed in overview, sets links and puts them in order
    """
    # single-view
    fieldsets = [
        ('Info',    {'fields': ['user']}),
        ('Content', {'fields': ['text', 'picture']}),
        ('Meta',   {'fields': ['hashtags', 'group', 'ignore', 'comment']}),
    ]
    # overview
    list_display = ('date', 'text', 'user', 'group')
    list_display_links = ('date', 'text')
    ordering = ('-date', 'user', 'group')


# initialize admin view for Notifications
class NTFCAdmin(admin.ModelAdmin):
    """
    fieldsets for single notification view
    - groups different fields and puts them in order
    sets attributes to be displayed in overview, sets links and puts them in order
    """
    # single-view
    fieldsets = [
        ('Meta',    {'fields': ['user', 'date', 'read']}),
        ('Content', {'fields': ['follower', 'group', 'message', 'comment', 'note']}),
    ]
    # overview
    list_display = ('date', 'user', 'note', 'read')
    list_display_links = ('date', 'note')
    ordering = ('-date', 'user', 'read')


class FAQAdmin(admin.ModelAdmin):
    """
    fieldsets for single frequently asked question view
    - groups different fields and puts them in order
    sets attributes to be displayed in overview, sets links and puts them in order
    """
    # single-view
    fieldsets = [
        ('Kategorie', {'fields': ['category']}),
        ('Frage',               {'fields': ['question', 'answer']}),
        ('Autor',               {'fields': ['author']}),
    ]
    # overview
    list_display = ('category', 'question', 'author')
    list_display_links = ('category', 'question')
    ordering = ('category', 'question')

# set attributes to be displayed in user overview
UserAdmin.list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'is_staff')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Message, MsgAdmin)
admin.site.register(Hashtag)
admin.site.register(GroupProfile, GroupAdmin)
admin.site.register(Notification, NTFCAdmin)
admin.site.register(FAQ, FAQAdmin)                  # register FAQ for admin page
