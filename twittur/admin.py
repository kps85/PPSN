from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


from .models import UserProfile, Message, Group, Favorite, ToGroup, ToUser, Has, Hashtag 
# Register your models here.

UserAdmin.list_display = ('username' ,'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'is_staff')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile)
admin.site.register(Message)
admin.site.register(Group)
admin.site.register(Favorite)
admin.site.register(ToGroup)
admin.site.register(ToUser)
admin.site.register(Has)
admin.site.register(Hashtag)