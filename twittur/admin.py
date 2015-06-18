from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import UserProfile, Message, Hashtag, FAQ, GroupProfile, Notification


# initialize admin view for FAQs
class FAQAdmin(admin.ModelAdmin):
    # set fields and order of them for FAQ overview
    fieldsets = [
        ('Kategorie', {'fields': ['category']}),
        ('Frage',               {'fields': ['question', 'answer']}),
        ('Autor',               {'fields': ['author']}),
    ]
    list_display = ('question', 'category', 'author')


UserAdmin.list_display = ('username' ,'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'is_staff')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile)
admin.site.register(Message)
admin.site.register(Hashtag)
admin.site.register(GroupProfile)
admin.site.register(Notification)
admin.site.register(FAQ, FAQAdmin) # register FAQ for admin page