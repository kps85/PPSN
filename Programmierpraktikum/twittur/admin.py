from django.contrib import admin

from .models import UserProfile, Message, Group, Favorite, ToGroup, ToUser, Has, Hashtag
# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Message)
admin.site.register(Group)
admin.site.register(Favorite)
admin.site.register(ToGroup)
admin.site.register(ToUser)
admin.site.register(Has)
admin.site.register(Hashtag)