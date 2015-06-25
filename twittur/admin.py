from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import FAQ, GroupProfile, Hashtag, Message, Notification, UserProfile


# initialize admin view for FAQs
class UserProfileAdmin(admin.ModelAdmin):
    # set fields and order of them for Group overview
    fieldsets = [
        ('User',    {'fields': ['userprofile']}),
        ('Info',    {'fields': ['picture', 'academicDiscipline', 'studentNumber', 'location', 'safety']}),
        ('Other',   {'fields': ['ignoreM', 'ignoreU', 'ignore']}),
    ]
    list_display = ('studentNumber', 'userprofile', 'academicDiscipline')
    list_display_links = ('studentNumber', 'userprofile')
    ordering = ('academicDiscipline', 'studentNumber', 'userprofile')


# initialize admin view for FAQs
class GroupAdmin(admin.ModelAdmin):
    # set fields and order of them for Group overview
    fieldsets = [
        ('SuperGroup',  {'fields': ['supergroup']}),
        ('Info',        {'fields': ['name', 'short', 'desc', 'password', 'picture', 'date', 'member', 'joinable']}),
        ('Admin',       {'fields': ['admin']}),
    ]
    list_display = ( 'name','supergroup', 'admin')
    list_display_links = ('supergroup', 'name')
    ordering = ('-supergroup', 'name')


# initialize admin view for FAQs
class MsgAdmin(admin.ModelAdmin):
    # set fields and order of them for Group overview
    fieldsets = [
        ('Info',    {'fields': ['user']}),
        ('Content', {'fields': ['text', 'picture']}),
        ('Meta',   {'fields': ['hashtags', 'group', 'ignore', 'comment']}),
    ]
    list_display = ('date', 'text', 'user', 'group')
    list_display_links = ('date', 'text')
    ordering = ('-date', 'user', 'group')


# initialize admin view for FAQs
class NTFCAdmin(admin.ModelAdmin):
    # set fields and order of them for Group overview
    fieldsets = [
        ('Meta',    {'fields': ['user', 'date', 'read']}),
        ('Content', {'fields': ['follower', 'group', 'message', 'comment', 'note']}),
    ]
    list_display = ('date', 'user', 'note', 'read')
    list_display_links = ('date', 'note')
    ordering = ('-date', 'user', 'read')


# initialize admin view for FAQs
class FAQAdmin(admin.ModelAdmin):
    # set fields and order of them for FAQ overview
    fieldsets = [
        ('Kategorie', {'fields': ['category']}),
        ('Frage',               {'fields': ['question', 'answer']}),
        ('Autor',               {'fields': ['author']}),
    ]
    list_display = ('category', 'question', 'author')
    list_display_links = ('category', 'question')
    ordering = ('category', 'question')


UserAdmin.list_display = ('username' ,'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'is_staff')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Message, MsgAdmin)
admin.site.register(Hashtag)
admin.site.register(GroupProfile, GroupAdmin)
admin.site.register(Notification, NTFCAdmin)
admin.site.register(FAQ, FAQAdmin) # register FAQ for admin page