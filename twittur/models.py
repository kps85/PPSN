from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save


#### Entitys

# - user
class UserProfile(models.Model):

    userprofile = models.OneToOneField(User)

    studentNumber = models.IntegerField(default=0)
    academicDiscipline = models.CharField( max_length = 200 )
    picture = models.ImageField(verbose_name = 'Profilbild', upload_to = 'picture/', blank=True,
                                height_field = None, width_field = None, default='picture/default.gif',
                                help_text = 'Dieses Bild wird auf Deinem Profil und in deinen Nachrichten angezeigt.')

    location = models.CharField( max_length = 200, default='' )
    
    def __str__(self):
        return self.userprofile.username + ' (' + self.userprofile.first_name + ' ' + self.userprofile.last_name +')'


# - message from User (message_from_self) to User (message_to_user)
class Message(models.Model):
    user = models.ForeignKey( settings.AUTH_USER_MODEL ) # who write this shit?
    text = models.CharField( max_length = 254 )
    picture = models.ImageField(upload_to = 'picture/', height_field = None, width_field = None, blank=True)
    date = models.DateTimeField( 'date published' )
    
    def __str__(self):
        return self.user.username + ': ' + '"' + self.text + '"'

# - groups 
class Group(models.Model):
    name = models.CharField( max_length = 50 )
    description = models.CharField( max_length = 256 )
    picture = models.ImageField( upload_to = 'picture/', blank=True, default='picture/defaultG.gif')
    date = models.DateTimeField( 'date published' )
    superGroup = models.ForeignKey( 'self',  blank = True, null = True )

    def __str__(self):
        return self.name 

class Hashtag(models.Model):
    name = models.CharField( max_length = 50 )

    def __str__(self):
        return '#' + self.name


#### Relationships

# - user (follow_from_self) follows user (follow_to_user)
class Favorite(models.Model):
    fromUser = models.ForeignKey( settings.AUTH_USER_MODEL, related_name = 'favorite_from' )
    toUser = models.ForeignKey( settings.AUTH_USER_MODEL, related_name = 'favorite_to' )

    def __str__(self):
        return self.fromUser.name + ' -> ' + self.toUser.name


# - message directed to group or user or both
class ToGroup(models.Model):
    group = models.ForeignKey( Group )
    message = models.ForeignKey( Message )

    def __str__(self):
        return "Message from '" + self.message.user.username + "' to group " + self.group.name
 
class ToUser(models.Model): 
    toUser = models.ForeignKey( settings.AUTH_USER_MODEL )
    message = models.ForeignKey( Message )

    def __str__(self):
        return "Message from " + self.message.user.username + " to " + self.toUser.name  

class IsInGroup(models.Model):

    user = models.ForeignKey( settings.AUTH_USER_MODEL )
    group = models.ForeignKey( Group )
    #isInGroup_superuser = models.Boolean( default = False )

    def __str__(self):
        return self.user.name + ' joint the group ' + self.group.name

class Has(models.Model):
    message = models.ForeignKey( Message )
    hashtag = models.ForeignKey( Hashtag )

    def __str__(self):
        return self.message.user.name + "'s' message contains #" + self.hashtag.name

# Navbar     
class Nav(models.Model):
    nav = [
        {'name':'index','title':'Startseite'},
        {'name':'profile','title':'Profil'},
        {'name':'info','title':'Info'},
        {'name':'settings','title':'Einstellungen'},
        {'name':'logout','title':'Logout'}
    ]
    


