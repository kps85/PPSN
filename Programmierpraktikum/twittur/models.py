from django.db import models



#### Entitys

# - user
class User(models.Model):
    user_name = models.CharField( max_length = 50 )
    user_email = models.CharField (max_length = 20 )
    user_password = models.EmailField( max_length = 254 )
    user_picture = models.ImageField( upload_to = None, max_length = 100 )
    user_joinDate = models.DateTimeField( 'date published' )

# - publicly tweet from user (tweet_user)
class Tweet(models.Model):
    tweet_date = models.DateTimeField( 'date published' )
    tweet_text = models.CharField( max_length = 254 )
    tweet_picture = models.FileField( upload_to = None, height_field = None, width_field = None, max_length = 100 )
    tweet_user = models.ForeignKey( User )

# - private message from User (message_from_self) to User (message_to_user)
class Message(models.Model):
    message_date = models.DateTimeField( 'date published' )
    message_text = models.CharField( max_length = 254 )
    message_picture = models.ImageField( upload_to = None, height_field = None, width_field = None, max_length = 100 )
    message_from_self = models.ForeignKey( User )
    message_to_user = models.ForeignKey( User )

# - hashtagtext
class Hashtag(models.Model):
    hashtag_text = models.CharField( max_length = 254 )

#### Relationships

# - user (follow_from_self) follows user (follow_to_user)
class Follow(models.Model):
    follow_from_self = models.ForeignKey( User )
    follow_to_user = models.ForeignKey( User )

# - tweet (has_tweet) contains hashtag (has_hashtag)
class Has(model.Model):
    has_tweet = models.ForeignKey( Tweet )
    has_hashtag = models.ForeignKey( Hashtag )

&