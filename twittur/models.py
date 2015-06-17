from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from datetime import date

#### Entitys


# - user
class UserProfile(models.Model):
    userprofile = models.OneToOneField(User)

    follow = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='follow')
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

    def __str__(self):
        return self.userprofile.username + ' (' + self.userprofile.first_name + ' ' + self.userprofile.last_name + ')'

    def delete(self, using=None):
        print(self)
        if self.picture != 'picture/default.gif':
            self.picture.delete()
        super(UserProfile, self).delete()

class GroupProfile(models.Model):
    name = models.CharField(max_length=50)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL)
    desc = models.CharField(max_length=200)
    picture = models.ImageField(verbose_name='Profilbild', upload_to='picture/', blank=True,
                                height_field=None, width_field=None, default='picture/gdefault.gif',
                                help_text='Geben sie ein Foto ein!')
    date = models.DateField(default=date.today)

    def __str__(self):
        return self.name




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
    attags = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='attags')

    def __str__(self):
        return self.user.username + ': ' + '"' + self.text + '"'



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
        {'name': 'info', 'title': 'Info'},
        {'name': 'settings', 'title': 'Einstellungen'},
        {'name': 'logout', 'title': 'Logout'}
    ]
