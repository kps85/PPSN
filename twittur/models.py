from datetime import date

from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from django.utils import timezone

#### Entitys
class Hashtag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# - message from User (message_from_self) to User (message_to_user)
class Message(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)  # author
    text = models.CharField(max_length=254)
    picture = models.ImageField(upload_to='picture/', height_field=None, width_field=None, blank=True)
    date = models.DateTimeField('date published')
    hashtags = models.ManyToManyField(Hashtag, related_name='hashtags')
    attags = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='attags', through='Notification')
    comment = models.ForeignKey('self', related_name='comments', blank=True, null=True)
    ignore = models.BooleanField(default=False)

    def get_model_name(self):
                return self.__class__.__name__

    def __str__(self):
        return self.user.username + ': ' + '"' + self.text + '"'


# - user
class UserProfile(models.Model):
    userprofile = models.OneToOneField(User)

    follow = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='follow', through='Notification')
    studentNumber = models.CharField(max_length=6, default='000000',
                                     help_text='&Uuml;ber deine Matrikel-Nummer kannst Du eindeutig als Student der '
                                               'TU Berlin identifiziert werden.<br>(only numbers, max. 6 chars)')
    academicDiscipline = models.CharField(max_length=200,
                                          help_text='&Uuml;ber deinen Studiengang wirst Du '
                                                    'bestimmten Gruppen zugeordnet.')
    picture = models.ImageField(verbose_name='Profilbild', upload_to='picture/', blank=True,
                                height_field=None, width_field=None, default='picture/default.gif',
                                help_text='Dieses Bild wird auf Deinem Profil (gro&szlig;) '
                                          'und in deinen Nachrichten (klein) angezeigt.')

    location = models.CharField(max_length = 200, default='None', help_text='Lass Deine KommilitonInnen Dich finden!')
    ignoreM = models.ManyToManyField(Message, related_name='ignoreM')
    ignoreU = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='ignoreU')
    ignore = models.BooleanField(default=False)

    def __str__(self):
        return self.userprofile.username + ' (' + self.userprofile.first_name + ' ' + self.userprofile.last_name + ')'

    def delete(self, using=None):
        if self.picture != 'picture/default.gif':
            self.picture.delete()
        super(UserProfile, self).delete()


class GroupProfile(models.Model):
    name = models.CharField(max_length=50)
    short = models.CharField(max_length=10)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='admin')
    desc = models.CharField(max_length=200)
    password = models.CharField(max_length=128, blank=True,
                                help_text='Geben Sie ein Passwort zum Beitreten ihrer Gruppe ein. (optional)')
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='admin')
    picture = models.ImageField(verbose_name='Gruppenbild', upload_to='picture/', blank=True,
                                height_field=None, width_field=None, default='picture/gdefault.gif',
                                help_text='Dieses Bild wird auf der Gruppenseite zu sehen sein!')
    date = models.DateField(default=date.today, blank=True)
    member = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='member')

    def __str__(self):
        return self.name


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='ntfcUser')
    follower = models.ForeignKey(UserProfile, related_name='ntfcFollower', blank=True, null=True)
    group = models.ForeignKey(GroupProfile, related_name='ntfcGroup2', blank=True, null=True)
    message = models.ForeignKey(Message, related_name='ntfcMessage', blank=True, null=True)
    comment = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)
    note = models.TextField(default=None, blank=True)

    def __str__(self):
        if self.follower:
            return self.follower.userprofile.username + ' to ' + self.user.username
        elif self.group:
            return 'Group Notification: ' + self.group.short + ' -> "' + self.user.username + '".'
        elif self.message and not self.comment:
            return self.user.username + ' mentioned in message: "' + self.message.text + '".'
        elif self.message and self.comment:
            return self.message.user.username + ' replied to ' + self.user.username + '.'

    def get_model_name(self):
        return self.__class__.__name__


# FAQ model
# - author: FAQ respondent REFERENCES User
# - question: a frequently asked question
# - category: a category the question is assigned to by the respondent
# - answer: an answer the respondent has given
class FAQ(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    question = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    answer = models.TextField(max_length=1000)


# Navbar
class Nav(models.Model):
    nav = [
        {'name': 'index', 'title': 'Startseite'},
        {'name': 'profile', 'title': 'Profil'},
        {'name': 'notification', 'title': 'Mitteilungen'},
        {'name': 'info', 'title': 'Info'},
        #{'name': 'settings', 'title': 'Einstellungen'},
        {'name': 'logout', 'title': 'Logout'}
    ]
