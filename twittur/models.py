"""
-*- coding: utf-8 -*-
@package twittur
@author twittur-Team (Lilia B., Ming C., William C., Karl S., Thomas T., Steffen Z.)
Models
- Hashtag       a hashtag represents a topic mentioned in a message
- GroupProfile  model for a group
- Message       model for a message (comments are messages with the comment attribute set)
- UserProfile   specific user data
- Notification  notification model
- FAQ           frequently asked question
- Nav           navigation bar elements
"""

from datetime import date

from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from django.utils import timezone


class Hashtag(models.Model):
    """ a hashtag represents a specific topic, which can be added to a message """
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class GroupProfile(models.Model):
    """
    a group can be password protected as well as not joinable (for automatic generated groups like TU Berlin,
    the faculty groups or specific academic discipline groups, as well as it can have a supergroup
    """
    name = models.CharField(max_length=50)
    short = models.CharField(max_length=10)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='admin')
    desc = models.CharField(max_length=200)
    password = models.CharField(max_length=128, blank=True,
                                help_text='Geben Sie ein Passwort zum Beitreten ihrer Gruppe ein. (optional)')
    picture = models.ImageField(verbose_name='Gruppenbild', upload_to='picture/', blank=True,
                                height_field=None, width_field=None, default='picture/gdefault.gif',
                                help_text='Dieses Bild wird auf der Gruppenseite zu sehen sein!')
    date = models.DateField(default=date.today, blank=True)
    member = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='member')
    joinable = models.BooleanField(default=True)
    supergroup = models.ForeignKey('self', related_name='sgroup', blank=True, null=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class Message(models.Model):
    """ a message can also have topics, targets (user or groups) and a parent message (comment) """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)  # author
    text = models.CharField(max_length=254)
    picture = models.ImageField(upload_to='picture/', height_field=None, width_field=None, blank=True)
    date = models.DateTimeField('date published')
    hashtags = models.ManyToManyField(Hashtag, related_name='hashtags')
    attags = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='attags', through='Notification')
    group = models.ForeignKey(GroupProfile, related_name='group', blank=True, null=True)
    comment = models.ForeignKey('self', related_name='comments', blank=True, null=True)
    ignore = models.BooleanField(default=False)

    def get_model_name(self):
        return self.__class__.__name__

    def __unicode__(self):
        return self.user.username + ': ' + '"' + self.text + '"'

    def __str__(self):
        return self.user.username + ': ' + '"' + self.text + '"'


class UserProfile(models.Model):
    """ the user profile contains additional information for a user """
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

    location = models.CharField(max_length=200, default='None', help_text='Lass Deine KommilitonInnen Dich finden!')
    ignoreM = models.ManyToManyField(Message, related_name='ignoreM', blank=True)
    ignoreU = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='ignoreU', blank=True)
    ignore = models.BooleanField(default=False)
    safety = models.CharField(max_length=15, default='public')

    def __unicode__(self):
        return self.userprofile.username + ' (' + self.userprofile.first_name + ' ' + self.userprofile.last_name + ')'

    def __str__(self):
        return self.userprofile.username + ' (' + self.userprofile.first_name + ' ' + self.userprofile.last_name + ')'

    def delete(self, using=None):
        if self.picture != 'picture/default.gif':
            self.picture.delete()
        super(UserProfile, self).delete()


class Notification(models.Model):
    """ a notification for different events on the page """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='ntfcUser')
    follower = models.ForeignKey(UserProfile, related_name='ntfcFollower', blank=True, null=True)
    group = models.ForeignKey(GroupProfile, related_name='ntfcGroup2', blank=True, null=True)
    message = models.ForeignKey(Message, related_name='ntfcMessage', blank=True, null=True)
    comment = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)
    note = models.TextField(default=None, blank=True)

    def __unicode__(self):
        if self.follower:
            return self.follower.userprofile.username + ' to ' + self.user.username
        elif self.group:
            return 'Group Notification: ' + self.group.short + ' -> "' + self.user.username + '".'
        elif self.message and not self.comment:
            return self.user.username + ' mentioned in message: "' + self.message.text + '".'
        elif self.message and self.comment:
            return self.message.user.username + ' replied to ' + self.user.username + '.'

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


class FAQ(models.Model):
    """ a frequently asked question, which is shown on the FAQ info page """
    author = models.ForeignKey(settings.AUTH_USER_MODEL)    # FAQ respondent REFERENCES User
    question = models.CharField(max_length=100)             # a frequently asked question
    category = models.CharField(max_length=100)             # a category the question is assigned to by the respondent
    answer = models.TextField(max_length=1000)              # an answer the respondent has given


class Nav(models.Model):
    """ returns a list of navigation bar elements, which are shown on every page for logged-in users """
    nav = [
        {'name': 'index', 'title': 'Startseite'},
        {'name': 'profile', 'title': 'Profil'},
        {'name': 'notification', 'title': 'Mitteilungen'},
        
        {'name': 'info', 'title': 'Info'},
        {'name': 'settings', 'title': 'Einstellungen'},
        {'name': 'logout', 'title': 'Logout'}
    ]
