import random, re

from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from itertools import chain
from operator import attrgetter

from .models import UserProfile, Nav, Message, Hashtag, GroupProfile, NotificationM, NotificationF
from .forms import UserForm, UserDataForm #,CommentForm
from .functions import editMessage, getMessages, getMessagesEnd, msgDialog, pw_generator, getNotificationCount #, commentMessage


# startpage
def index(request):
    # check if user is logged in
    # if user is not logged in, redirect to FTU
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    has_msg, success_msg, list_end, end = False, None, False, 5

    current_user = User.objects.filter(username__exact=request.user.username).select_related('userprofile')
    user_list = UserProfile.objects.filter(userprofile__exact=request.user)
    #    atTag = '@' + request.user.username + ' '

    msgForm = msgDialog(request)
    #cmForm = commentMessage(request)

    if request.method == 'POST':
        success_msg = editMessage(request)
    elif request.method == 'GET' and 'last' in request.GET:
        end = getMessagesEnd(data={'last': request.GET.get('last'), 'page': 'index', 'user': current_user})

        # Messages
        messages = getMessages(data={'page': 'index', 'user': current_user, 'end': end})
        message_list = zip(
            messages['message_list'][:end], messages['dbmessage_list'][:end],
            messages['comment_list'], messages['comment_count']
        )

        if end > len(messages['message_list']):
            list_end = True

        context = {'active_page': 'index', 'user': current_user, 'list_end': list_end,
                   'message_list': message_list, 'msgForm': msgForm}
        return render(request, 'message_box_reload.html', context)

    # Messages
    messages = getMessages(data={'page': 'index', 'user': current_user, 'end': end})
    if end > len(messages['message_list']):
        list_end = True
    if 'has_msg' in messages:
        has_msg = True
    message_list = zip(
        messages['message_list'][:end], messages['dbmessage_list'][:end],
        messages['comment_list'], messages['comment_count']
    )

    # Follow List
    curUser = UserProfile.objects.get(userprofile=request.user)
    follow_list = curUser.follow.all()
    # Group List
    group_sb_list = GroupProfile.objects.all().filter(Q(member__exact=request.user))
    # Beliebte Themen
    hot_list = Hashtag.objects.annotate(hashtag_count=Count('hashtags__hashtags__name')) \
                   .order_by('-hashtag_count')[:5]

    # Notification
    new = getNotificationCount(request.user)

    context = {
        'active_page': 'index',
        'current_user': current_user,
        'user_list': user_list,
        'message_list': message_list,
        'nav': Nav.nav,
        'msgForm': msgForm,
        'new': new,
        'success_msg': success_msg,
        'hot_list': hot_list,
        'follow_sb_list': sorted(follow_list, key=lambda x: random.random())[:5],
        'group_sb_list': group_sb_list,
        'has_msg': has_msg,
        'list_end': list_end,
    }
    return render(request, 'index.html', context)


# login/registration page
def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/')

    # Public Messages: TODO Filtern!
    message_list = Message.objects.filter(
        Q(comment=None) & Q(attags=None)
    ).order_by('-date')

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
                error_login = "Ups, Username oder Passwort falsch."
                active_toggle = "active_toggle"
                return render(request, 'ftu.html',
                              {'error_login': error_login, 'message_list': message_list, 'active_page': 'ftu'})

    # Registration
    if request.method == 'POST':
        query_dict, data, errors, success_msg = request.POST, {}, {}, None
        username, password, email, first_name, last_name, academicDiscipline, studentNumber = \
            None, None, None, None, None, None, None

        if 'password_reset' in request.POST:
            try:
                user = User.objects.get(email=request.POST['pwResetMail'])
                if request.POST['pwResetStudNumb'] == user.userprofile.studentNumber:
                    password = pw_generator(10)
                    message = "Hallo!\n" \
                              "\n" \
                              "Du hast ein neues Passwort fuer deinen Account bei twittur beantragt.\n" \
                              "\n" \
                              "Dein neues Passwort lautet: " + password + "\n" \
                              "\n" \
                              "Bitte aendere Dein Passwort schnellstmoeglich, indem Du dich mit dem oben genannten " \
                              "Passwort einloggst und unter Einstellungen ein neues Passwort festlegst.\n" \
                              "\n" \
                              "Wir freuen uns auf Deinen Besuch!\n" \
                              "\n" \
                              "Mit freundlichen Gruessen,\n" \
                              "Dein twittur Team!"
                    send_mail("PW Reset", message, "twittur.sn@gmail.com", [request.POST['pwResetMail']])
                    user.set_password(password)
                    user.save()
                    success_msg = 'Dein neues Passwort hast du per E-Mail erhalten!'
                else:
                    errors['error_number_not_identic'] = "Die eingegebene Matrikel-Nummer stimmt nicht mit der " \
                                                         "Matrikel-Nummer &uuml;berein, die uns bekannt ist.<br>" \
                                                         "Wenn Du Deine eingegebe Matrikel-Nummer vergessen hast, " \
                                                         "kontaktiere ein twittur-Teammmitglied. (siehe " \
                                                         "<a href='/twittur/info'>Impressum</a>)"
            except:
                errors['error_not_registered'] = "Die eingegebene E-Mail Adresse ist nicht registriert."

        else:
            userList, username, academicDiscipline, studentNumber, data, errors \
                = User.objects.all(), query_dict.get('name'), None, 0, {}, {}

            # case if username is available
            for user in userList:
                if username.lower() == user.username.lower():
                    errors['error_reg_user_n'] = "Sorry, Username ist vergeben."
            if 'error_reg_user_n' not in errors:
                if re.match("^[a-zA-Z0-9-_.]*$", username):
                    data['username'] = username
                else:
                    errors['error_reg_user_n'] = "Nur 'A-Z, a-z, 0-9, -, _' und '.' im Usernamen erlaubt!"

            # Password validation
            password = query_dict.get('password')
            ack_password = query_dict.get('ack_password')
            if password != ack_password:
                errors['error_reg_user_p'] = "Passw&ouml;rter sind nicht gleich."

            # EMail validation
            email = query_dict.get('email')
            mail = email.split('@')
            if len(mail) == 1 or not (
                        mail[1].endswith(".tu-berlin.de") or
                        (email[(len(email) - 13):len(email)] == '@tu-berlin.de')
            ):
                errors['error_reg_mail'] = "Keine g&uuml;tige TU E-Mail Adresse!"
            else:
                try:
                    checkMail = User.objects.get(email=email)
                    errors['error_reg_mail'] = "Ein Benutzer mit dieser E-Mail Adresse existiert bereits!"
                except:
                    data['email'] = email

            # fill the rest for modal User and Userprofile
            first_name = query_dict.get('first_name')
            if len(first_name) > 0:
                data['first_name'] = first_name
            last_name = query_dict.get('last_name')
            if len(last_name) > 0:
                data['last_name'] = last_name
            if len(query_dict.get('studentNumber')) == 6:
                studentNumber = query_dict.get('studentNumber')
                try:
                    checkSN = UserProfile.objects.get(studentNumber=studentNumber)
                    errors["error_student_number"] = "Ein Benutzer mit dieser Matrikel-Nummer existiert bereits."
                except:
                    data['studentNumber'] = studentNumber
            else:
                if len(query_dict.get('studentNumber')) > 0:
                    data['studentNumber'] = query_dict.get('studentNumber')
                errors['error_student_number'] = "Die eingegebene Matrikel-Nummer ist ung&uuml;ltig!"
            academicDiscipline = query_dict.get('academicDiscipline')
            if len(academicDiscipline) > 0:
                data['academicDiscipline'] = academicDiscipline
            else:
                errors['error_reg_userprofile_ad'] = "Bitte Studiengang ausw&auml;hlen!"

        # context for html
        context = {
            'active_page': 'ftu',
            'nav': Nav.nav,
            'message_list': message_list,
            'data': data,
            'errors': errors
        }

        # error?
        if len(errors) > 0 or 'password_reset' in request.POST:
            if 'password_reset' in request.POST:
                context['pActive'] = 'active'
                if success_msg:
                    context['success_msg'] = success_msg
            else:
                context['rActive'] = 'active'
            return render(request, 'ftu.html', context)

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
        return HttpResponseRedirect('/twittur/')

    context = {'active_page': 'ftu', 'nav': Nav.nav, 'message_list': message_list, 'active_page': 'ftu'}
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

    show_favs, has_msg, error_msg, success_msg, end, list_end = False, None, {}, None, 5, False

    # Follow List
    curUser = UserProfile.objects.get(userprofile=request.user)
    follow_list = curUser.follow.all()
    # Group List
    group_sb_list = GroupProfile.objects.all().filter(Q(member__exact=request.user))
    # Beliebte Themen
    hot_list = Hashtag.objects.annotate(hashtag_count=Count('hashtags__hashtags__name')) \
                   .order_by('-hashtag_count')[:5]
    # Notification
    new = getNotificationCount(request.user)

    if request.method == 'GET' and 'last' in request.GET:
        current_user = User.objects.get(username__exact=user)
        end = getMessagesEnd(data={'last': request.GET.get('last'), 'page': 'profile', 'user': current_user})

        # Messages
        msgForm = msgDialog(request)
        messages = getMessages(data={'page': 'profile', 'user': current_user, 'end': end})
        message_list = zip(
            messages['message_list'][:end], messages['dbmessage_list'][:end],
            messages['comment_list'], messages['comment_count']
        )

        if end >= len(messages['message_list']):
            list_end = True

        context = {'active_page': 'profile', 'user': request.user, 'list_end': list_end,
                   'message_list': message_list, 'msgForm': msgForm}
        return render(request, 'message_box_reload.html', context)

    try:
        newUser = User.objects.get(username=user)  # this is the user displayed in html

        # follow
        if request.method == "GET" and 'follow' in request.GET:
            if newUser in follow_list:
                print("remove")
                follow = NotificationF.objects.get(Q(me__exact=request.user.userprofile) & Q(you__exact=newUser))
                follow.delete()
                success_msg = 'Du folgst ' + user.upper() + ' jetzt nicht mehr.'
            else:
                print("add")
                curUser.save()
                notification = NotificationF(me=request.user.userprofile, you=newUser, read=False)
                notification.save()
                success_msg = 'Du folgst ' + user.upper() + ' jetzt.'

        if newUser in follow_list:
            follow_text = '<span class="glyphicon glyphicon-eye-close"></span> ' + user.upper() + ' nicht folgen'
        else:
            follow_text = '<span class="glyphicon glyphicon-eye-open"></span> ' + user.upper() + ' folgen'

        if request.method == 'POST':
            success_msg = editMessage(request)

        # Messages
        messages = getMessages(data={'page': 'profile', 'user': newUser, 'end': end})
        message_list = zip(
            messages['message_list'][:end], messages['dbmessage_list'][:end],
            messages['comment_list'], messages['comment_count']
        )

        if 'has_msg' in messages:
            has_msg = messages['has_msg']

        if 'favorits' in request.GET:
            show_favs = True

        context = {
            'active_page': 'profile',
            'nav': Nav.nav,
            'new': new,
            'show_favs': show_favs,
            'curUser': newUser,
            'curUserProfile': newUser.userprofile,
            'profileUser': user,
            'message_list': message_list,
            'msgForm': msgDialog(request),
            'has_msg': has_msg,
            'success_msg': success_msg,
            'hot_list': hot_list,
            'follow_list': follow_list,
            'follow_sb_list': sorted(follow_list, key=lambda x: random.random())[:5],
            'follow_text': follow_text,
            'group_sb_list': group_sb_list
        }

    except:
        error_msg['error_no_user'] = 'Kein Benutzer mit dem Benutzernamen ' + user + ' gefunden!'
        context = {
            'active_page': 'profile',
            'nav': Nav.nav,
            'curUser': None,
            'error_msg': error_msg,
            'hot_list': hot_list,
            'follow_list': follow_list,
            'follow_sb_list': sorted(follow_list, key=lambda x: random.random())[:5],
            'group_sb_list': group_sb_list
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

    # Notification
    new = getNotificationCount(request.user)

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
                if 'password' in request.POST and len(request.POST['password']) > 0:
                    username = request.POST['username']
                    password = request.POST['password']
                    user = authenticate(username=username, password=password)
                    auth.login(request, user)
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
        'new': new,
        'msgForm': msgDialog(request),
        'success_msg': success_msg,
        'error_msg': error_msg,
        'user': curUser,
        'userForm': userForm,
        'userDataForm': userDataForm
    }
    return render(request, 'settings.html', context)


def showMessage(request, msg):

    success_msg, error_msg, has_msg = None, {}, False

    # Follow List
    curUser = UserProfile.objects.get(userprofile=request.user)
    follow_list = curUser.follow.all()
    # Group List
    group_sb_list = GroupProfile.objects.all().filter(Q(member__exact=request.user))
    # Beliebte Themen
    hot_list = Hashtag.objects.annotate(hashtag_count=Count('hashtags__hashtags__name')) \
                   .order_by('-hashtag_count')[:5]
    # Notification
    new = getNotificationCount(request.user)


    msgForm = msgDialog(request)
    if request.method == 'POST':
        success_msg = editMessage(request)

    # Messages
    messages = getMessages(data={'page': msg, 'user': request.user, 'end': None})
    if 'has_msg' in messages:
        has_msg = messages['has_msg']
    message_list = zip(messages['message_list'], messages['dbmessage_list'], messages['comment_list'])

    # return relevant information to render message.html
    context = {
        'active_page': 'message',
        'msg_id': msg,
        'nav': Nav.nav,
        'new': new,
        'hot_list': hot_list,
        'follow_sb_list': sorted(follow_list, key=lambda x: random.random())[:5],
        'group_sb_list': group_sb_list,
        'msgForm': msgForm,
        'user': request.user,
        'success_msg': success_msg,
        'error_msg': error_msg,
        'message_list': message_list,
        'has_msg': has_msg
    }
    return render(request, 'message.html', context)


def notification(request):
    # for context
    notificationM_list = NotificationM.objects.all().filter(user=request.user)#.order_by('-message__date')
    notificationF_list = NotificationF.objects.all().filter(you=request.user)#.order_by('-message__date')
    notificationC_list = Message.objects.all().filter(comment__user=request.user).exclude(user=request.user)
    print(notificationF_list.all())
    print(notificationM_list.all())
    print(notificationC_list.all())

    notification_list = sorted(chain(notificationM_list, notificationF_list, notificationC_list), key=attrgetter('date') ,
    reverse=True)
    boolean_list = []


    # saving boolean extra, because it will deleted by next for loop
    for no in notification_list:
        if no.read == False:
            boolean_list.append('False')
        else:
            boolean_list.append('True')

    notification_list = zip(notification_list,boolean_list)
    #newM = NotificationM.objects.filter(Q(read=False) & Q(user=request.user)).count()
    #newF = NotificationF.objects.filter(Q(read=False) & Q(you=request.user)).count()
    #newC = Message.objects.all().filter(comment__user=request.user).count()
    #new = newF + newM + newC

    new = getNotificationCount(request.user)
    print(new)
    # Follow List
    curUser = UserProfile.objects.get(userprofile=request.user)
    follow_list = curUser.follow.all()
    # Group List
    group_sb_list = GroupProfile.objects.all().filter(Q(member__exact=request.user))
    # Beliebte Themen
    hot_list = Hashtag.objects.annotate(hashtag_count=Count('hashtags__hashtags__name')) \
                   .order_by('-hashtag_count')[:5]

    context = {
        'active_page': 'notification',
        'nav': Nav.nav,
        'user': request.user,
        'notification_list': notification_list,
        'new': new,
        'hot_list': hot_list,
        'follow_sb_list': sorted(follow_list, key=lambda x: random.random())[:5],
        'group_sb_list': group_sb_list
    }

    # update -> set all notification to true
    for n in NotificationM.objects.filter(Q(read=False) & Q(user=request.user)):
        n.read = True
        n.save()
    for n in NotificationF.objects.filter(Q(read=False) & Q(you=request.user)):
        n.read = True
        n.save()
    for n in Message.objects.all().filter(Q(comment__user=request.user) & Q(read=False)).exclude(user=request.user):
        n.read = True
        n.save()
    return render(request, 'notification.html', context)