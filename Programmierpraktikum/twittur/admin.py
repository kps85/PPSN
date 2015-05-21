from django.contrib import admin

from .models import User, Message, Group, Favorite, ToGroup, ToUser
# Register your models here.

admin.site.register(User)
admin.site.register(Message)
admin.site.register(Group)
admin.site.register(Favorite)
admin.site.register(ToGroup)
admin.site.register(ToUser)