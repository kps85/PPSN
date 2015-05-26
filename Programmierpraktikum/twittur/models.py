from django.db import models



#### Entitys

# - user
class User(models.Model):
    name = models.CharField( max_length = 200 )
    nickname = models.CharField( max_length = 200 )
    email = models.EmailField( max_length = 200 )
    password = models.CharField( max_length = 200 )
    lastSeen = models.DateTimeField( 'last seen' )
    studentNumber = models.IntegerField(default=0)
    academicDiscipline = models.CharField( max_length = 200 )
    picture = models.ImageField( upload_to = 'profilPicture/', height_field = None, width_field = None, max_length = 100, blank=True)
    
    def __str__(self):
        return self.nickname + ' (' + self.name + ')'

# - message from User (message_from_self) to User (message_to_user)
class Message(models.Model):
    user = models.ForeignKey( User ) # who write this shit?
    text = models.CharField( max_length = 254 )
    picture = models.ImageField( upload_to = 'messagePicture/', height_field = None, width_field = None, max_length = 100, blank=True)
    date = models.DateTimeField( 'date published' )
    
    def __str__(self):
        return self.user.name + ': ' + '"' + self.text + '"'

# - groups 
class Group(models.Model):
    name = models.CharField( max_length = 50 )
    description = models.CharField( max_length = 256 )
    picture = models.ImageField( upload_to = 'profilPicture/', height_field = None, width_field = None, max_length = 100, blank=True)
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
    fromUser = models.ForeignKey( User, related_name = 'favorite_from' )
    toUser = models.ForeignKey( User, related_name = 'favorite_to' )

    def __str__(self):
        return self.fromUser.name + ' -> ' + self.toUser.name


# - message directed to group or user or both
class ToGroup(models.Model):
    group = models.ForeignKey( Group )
    message = models.ForeignKey( Message )

    def __str__(self):
        return "Message from '" + self.message.user.name + "' to group " + self.group.name 
 
class ToUser(models.Model): 
    toUser = models.ForeignKey( User )
    message = models.ForeignKey( Message )

    def __str__(self):
        return "Message from " + self.message.user.name + " to " + self.toUser.name  

class IsInGroup(models.Model):
    user = models.ForeignKey( User )
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
        {'name':'settings','title':'Einstellungen'}
    ]
    


