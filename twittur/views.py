import copy, datetime

from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from .models import UserProfile, Group, Nav, Message, Hashtag
from .forms import UserForm, UserDataForm
from .functions import dbm_to_m, editMessage, msgDialog

# startpage
def index(request):
    # check if user is logged in
    # if user is not logged in, redirect to FTU
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    success_msg = None

    user = User.objects.filter(username__exact=request.user.username).select_related('userprofile')
    print(user)
    user_list = UserProfile.objects.filter(userprofile__exact=request.user)
    print(user_list)
    #    atTag = '@' + request.user.username + ' '

    if request.method == 'POST':
        success_msg = editMessage(request)

    #    dbmessage_list = Message.objects.all().select_related('user__userprofile') \
    #        .filter(Q(user__exact=request.user) | Q(text__contains=atTag)).order_by('-date')
    dbmessage_list = Message.objects.all().select_related('user__userprofile').order_by('-date')

    hashtag_list = Hashtag.objects.annotate(hashtag_count=Count('hashtags__hashtags__name')) \
                       .order_by('-hashtag_count')[:5]

    curDate = timezone.make_aware(datetime.datetime.now() - datetime.timedelta(minutes=10),
                                  timezone.get_current_timezone())
    message_list = []
    for message in dbmessage_list:
        if message.date > curDate:
            message.editable = True
        copy_message = copy.copy(message)
        message_list.append(dbm_to_m(copy_message))
    message_list = zip(message_list, dbmessage_list)

    context = {'active_page': 'index', 'current_user': user, 'user_list': user_list,
               'message_list': message_list, 'nav': Nav.nav, 'msgForm': msgDialog(request),
               'success_msg': success_msg, 'hashtag_list': hashtag_list}
    return render(request, 'index.html', context)


# login/registration page
def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/')

    # Public Messages: TODO Filtern!
    message_list = Message.objects.all().order_by('-date')

    # login
    if request.method == "GET":

        if 'login' in request.GET:
            query_dict = request.GET
            username = query_dict.get('username')
            password = query_dict.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    return HttpResponseRedirect('/twittur/')
            else:
                error_login = "- Ups, Username oder Passwort falsch."
                active_toggle = "active_toggle"
                return render(request, 'ftu.html',
                              {'error_login': error_login, 'message_list': message_list, 'active_page': 'ftu'})

    # Registration
    if request.method == 'POST':

        query_dict = request.POST
        error_reg_user, error_reg_userprofil, error_reg_user_n, error_reg_user_p, error_reg_userprofile_e, \
        error_reg_userprofile_ad, error_reg_userprofile_nr, error_reg_mail = None, None, None, None, None, None, None, None

        username = query_dict.get('name')
        studentNumber = 0

        try:
            checkUsername = User.objects.get(username__exact=username)

        # case if username is available (checkUsername = None)
        except ObjectDoesNotExist:
            password = query_dict.get('password')
            ack_password = query_dict.get('ack_password')

            # Password validation
            if password != ack_password:
                error_reg_user_p = " - Passw&ouml;rter sind nicht gleich."

            email = query_dict.get('email')

            mail = email.split('@')
            if len(mail) == 1 or (not mail[1].endswith(".tu-berlin.de")):
                error_reg_mail = "Junge, gib Tu mail ein!"

            if len(query_dict.get('studentNumber')) > 0:  # if input is empty, keep default (0)
                studentNumber = query_dict.get('studentNumber')

            # context for html
            context = {
                'error_reg_user': error_reg_user,
                'error_reg_userprofile_e': error_reg_userprofile_e,
                'error_reg_mail': error_reg_mail,
                'error_reg_user_n': error_reg_user_n,
                'error_reg_user_p': error_reg_user_p,
                'error_reg_userprofile_ad': error_reg_userprofile_ad,
                'error_reg_userprofile_nr': error_reg_userprofile_nr,
                'rActive': 'active',
                'active_page': 'ftu', 'nav': Nav.nav, 'message_list': message_list
            }
            # error?
            if error_reg_userprofile_ad or error_reg_mail or error_reg_userprofile_nr or error_reg_user or error_reg_userprofil or error_reg_user_p or error_reg_userprofile_e:
                return render(request, 'ftu.html', context)

            # fill the rest for modal User and Userprofile
            first_name = query_dict.get('first_name')
            last_name = query_dict.get('last_name')
            academicDiscipline = query_dict.get('academicDiscipline')
            studentNumber = query_dict.get('studentNumber')

            # create User and Userprofile
            user = User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            user_profil = UserProfile(userprofile=user, studentNumber=studentNumber,
                                      academicDiscipline=academicDiscipline, location="Irgendwo")
            user_profil.save()

            # log user in and redirect to index page
            user = authenticate(username=username, password=password)
            auth.login(request, user)
            return render(request, 'index.html', context)

        # case if username is taken (checkUsername == user)
        else:
            error_reg_user_n = "Sorry, Username ist vergeben."
            return render(request, 'ftu.html',
                          {'active_page': 'ftu', 'nav': Nav.nav, 'error_reg_user_n': error_reg_user_n,
                           'error_reg_mail': error_reg_mail, 'rActive': 'active'})

    context = {'active_page': 'ftu', 'nav': Nav.nav, 'message_list': message_list}
    return render(request, 'ftu.html', context)


# logout
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/twittur/')


# profilpage
def profile(request, user):
    # check if user is logged in
    # if user is not logged in, redirect to FTU
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    curUser = User.objects.get(username=user)
    curUserProfile = curUser.userprofile
    success_msg = None

    if request.method == 'POST':
        success_msg = editMessage(request)

    user_list = User.objects.all()
    group_list = Group.objects.all()

    dbmessage_list = Message.objects.all().select_related('user__userprofile') \
        .filter(Q(user__exact=curUser) | Q(attags__username__exact=curUser.username)
                ).order_by('-date').distinct()

    curDate = timezone.make_aware(datetime.datetime.now() - datetime.timedelta(minutes=10),
                                  timezone.get_current_timezone())
    message_list = []
    for message in dbmessage_list:
        if message.date > curDate:
            message.editable = True
        copy_message = copy.copy(message)
        message_list.append(dbm_to_m(copy_message))
    message_list = zip(message_list, dbmessage_list)

    context = {'curUser': curUser,
               'curUserProfile': curUserProfile,
               'active_page': 'profile',
               'profileUser': user,
               'dbmessage_list': dbmessage_list,
               'user_list': user_list,
               'group_list': group_list,
               'nav': Nav.nav,
               'message_list': message_list,
               'msgForm': msgDialog(request),
               'success_msg': success_msg
               }
    return render(request, 'profile.html', context)


# Page: 'Einstellungen'
# - allows: editing editable user information and deleting account
# -- picture, email, password, first_name, last_name,
#    academicDiscipline, studentNumber, location
# - template: info_support.html
def settings(request):
    # check if user is logged in
    # if user is not logged in, redirect to FTU
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    # get current users information and initialize return messages
    curUser = User.objects.get(pk=request.user.id)
    curUserProfile = curUser.userprofile
    success_msg, error_msg, userForm, userDataForm = None, None, None, None

    # check if account should be deleted
    # if true: delete account, return to FTU
    if request.method == 'POST' and request.POST['delete'] == 'true':
        curUser.userprofile.delete()
        curUser.delete()
        return HttpResponseRedirect('/twittur/')
    # else: validate userForm and userDataForm and save changes
    elif request.method == 'POST':
        userForm = UserForm(request.POST, instance=curUser)
        if userForm.is_valid():
            userDataForm = UserDataForm(request.POST, request.FILES, instance=curUserProfile)
            userDataForm.oldPicture = curUserProfile.picture
            # if picture has changed, delete old picture
            # do not, if old picture was default picture
            if 'picture' in request.FILES or 'picture-clear' in request.POST:
                if userDataForm.oldPicture != 'picture/default.gif':
                    userDataForm.oldPicture.delete()
            if userDataForm.is_valid():
                userForm.save()
                userDataForm.save()
                success_msg = 'Benutzerdaten wurden erfolgreich aktualisiert.'
            else:
                # return errors if userDataForm is not valid
                error_msg = userDataForm.errors
        else:
            # return errors if userForm is not valid
            error_msg = userForm.errors

    # initialize UserForm and UserDataForm with current users information
    userForm = UserForm(instance=curUser)
    userDataForm = UserDataForm(instance=curUserProfile)

    # return relevant information to render settings.html
    context = {
        'active_page': 'settings',
        'nav': Nav.nav,
        'msgForm': msgDialog(request),
        'success_msg': success_msg,
        'error_msg': error_msg,
        'user': curUser,
        'userForm': userForm,
        'userDataForm': userDataForm
    }
    return render(request, 'settings.html', context)