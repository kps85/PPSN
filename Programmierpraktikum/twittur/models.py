from django.db import models



#### Entitys

# - user
class User(models.Model):
    user_name = models.CharField( max_length = 200 )
    user_nickname = models.CharField( max_length = 200 )
    user_email = models.EmailField( max_length = 200 )
    user_password = models.CharField( max_length = 200 )
    user_lastSeen = models.DateTimeField( 'last seen' )
    user_mnr = models.IntegerField(default=0)
    user_academic_discipline = models.CharField( max_length = 200 )
    user_picture = models.ImageField( upload_to = None, height_field = None, width_field = None, max_length = 100, blank=True)
    
    def __str__(self):
        return self.user_nickname + ' (' + self.user_name + ')'

# - message from User (message_from_self) to User (message_to_user)
class Message(models.Model):
    message_from = models.ForeignKey( User ) # who write this shit?
    message_text = models.CharField( max_length = 254 )
    message_picture = models.ImageField( upload_to = None, height_field = None, width_field = None, max_length = 100, blank=True)
    message_date = models.DateTimeField( 'date published' )
    
    def __str__(self):
        return self.message_from.user_name + ': ' + '"' + self.message_text + '"'

# - groups 
class Group(models.Model):
    group_name = models.CharField( max_length = 50 )
    group_description = models.CharField( max_length = 256 )
    group_picture = models.ImageField( upload_to = None, height_field = None, width_field = None, max_length = 100, blank=True)
    group_date = models.DateTimeField( 'date published' )
    group_super = models.ForeignKey( 'self',  blank = True, null = True )

    def __str__(self):
        return self.group_name 

class Hashtag(models.Model):
    hashtag_name = models.CharField( max_length = 50 )

    def __str__(self):
        return '#' + self.hashtag_name


#### Relationships

# - user (follow_from_self) follows user (follow_to_user)
class Favorite(models.Model):
    favorite_from = models.ForeignKey( User, related_name = 'favorite_from' )
    favorite_to = models.ForeignKey( User, related_name = 'favorite_to' )

    def __str__(self):
        return self.favorite_from.user_name + ' -> ' + self.favorite_to.user_name


# - message directed to group or user or both
class ToGroup(models.Model):
    toGroup_user = models.ForeignKey( User ) 
    toGroup_group = models.ForeignKey( Group )
    toGroup_message = models.ForeignKey( Message )

    def __str__(self):
        return "Message from '" + self.toGroup_user.user_name + "' to group '" + self.toGroup_group.group_name + "'"
 
class ToUser(models.Model):
    toUser_from = models.ForeignKey( User, related_name = 'toUser_from' ) 
    toUser_to = models.ForeignKey( User, related_name = 'toUser_to' )
    toUser_message = models.ForeignKey( Message )

    def __str__(self):
        return "Message from " + self.toUser_from.user_name + " to User " + self.toUser_to.user_name  

class IsInGroup(models.Model):
    isInGroup_user = models.ForeignKey( User )
    isInGroup_group = models.ForeignKey( Group )
    #isInGroup_superuser = models.Boolean( default = False )

    def __str__(self):
        return self.isInGroup_superuser + ' joint the group ' + self.isInGroup_group

class Has(models.Model):
    has_message = models.ForeignKey( Message )
    has_hashtag = models.ForeignKey( Hashtag )

    def __str__(self):
        return self.has_message.message_from.user_name + "'s' message contains #" + self.has_hashtag.hashtag_name
    


