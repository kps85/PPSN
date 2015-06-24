import random, re

from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from .models import GroupProfile, UserProfile, Nav, Message, Notification
from .forms import UserForm, UserDataForm
from .functions import editMessage, getMessages, getWidgets, setNotification, pw_generator


# startpage
def index(request):
    # check if user is logged in
    # if user is not logged in, redirect to FTU
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    # initialize newMsgForm, user and various information
    user = User.objects.filter(username__exact=request.user.username).select_related('userprofile')

    # initialize sidebar lists
    widgets = getWidgets(request)

    context = {
        'active_page': 'index', 'nav': Nav.nav, 'new': widgets['new'], 'msgForm': widgets['msgForm'],
        'current_user': user, 'list_end': 5,
        'hot_list': widgets['hot_list'], 'group_sb_list': widgets['group_sb_list'],
        'follow_sb_list': sorted(widgets['follow_list'], key=lambda x: random.random())[:5]
    }

    # if request was sent to view: return success message
    if request.method == 'POST':
        context['success_msg'] = editMessage(request)
        if 'list_end' in request.POST:
            context['list_end'] = request.POST['list_end']

    # Messages
    messages = getMessages(data={'page': 'index', 'data': user, 'end': context['list_end'], 'request': request})
    context['message_list'] = messages['message_list']
    context['has_msg'] = messages['has_msg']

    return render(request, 'index.html', context)


# login/registration page
def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/')

    # Public Messages:
    message_list = Message.objects.filter(
        Q(comment=None) & Q(attags=None)
    ).order_by('-date')

    # login
    if request.method == "GET":
        if 'login' in request.GET:
            username = request.GET.get('username')
            password = request.GET.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    return HttpResponseRedirect('/twittur/')
            else:
                error_login = "Ups, Username oder Passwort falsch."
                return render(request, 'ftu.html',
                              {'active_page': 'ftu', 'error_login': error_login, 'message_list': message_list})

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
            userList, username = User.objects.all(), query_dict.get('name')

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
                mail[1].endswith(".tu-berlin.de") or (email[(len(email) - 13):len(email)] == '@tu-berlin.de')):
                errors['error_reg_mail'] = "Keine g&uuml;tige TU E-Mail Adresse!"
            else:
                try:
                    User.objects.get(email=email)
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
                    UserProfile.objects.get(studentNumber=studentNumber)
                    errors["error_student_number"] = "Ein Benutzer mit dieser Matrikel-Nummer existiert bereits."
                except:
                    data['studentNumber'] = studentNumber
            else:
                errors['error_student_number'] = "Die eingegebene Matrikel-Nummer ist ung&uuml;ltig!"
            academicDiscipline = query_dict.get('academicDiscipline')
            if len(academicDiscipline) > 0:
                data['academicDiscipline'] = academicDiscipline
            else:
                errors['error_reg_userprofile_ad'] = "Bitte Studiengang ausw&auml;hlen!"

        # context for html
        context = {
            'active_page': 'ftu', 'nav': Nav.nav, 'data': data, 'errors': errors,
            'message_list': message_list
        }

        # error?
        if len(errors) > 0 or 'password_reset' in request.POST:
            if 'password_reset' in request.POST:
                context['pActive'] = 'active'
                if success_msg: context['success_msg'] = success_msg
            else:
                context['rActive'] = 'active'
            return render(request, 'ftu.html', context)

        # create User and Userprofile
        user = User.objects.create_user(username, email, password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        userProfile = UserProfile(userprofile=user, studentNumber=studentNumber,
                                  academicDiscipline=academicDiscipline, location="Irgendwo")
        userProfile.save()

        # academic discipline (required user in db) -> add user to group uni, fac whatever and his academic discipline
        print(academicDiscipline)
        try:
            group = GroupProfile.objects.get(name=academicDiscipline)
            while True:
                group.member.add(user)
                if group.supergroup == None:
                    break
                else:
                    group = group.supergroup

        except:
            print("error, something went wrong")
            pass

        # log user in and redirect to index page
        user = authenticate(username=username, password=password)
        auth.login(request, user)
        return HttpResponseRedirect('/twittur/')

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

    error_msg, success_msg, end = {}, None, 5

    # initialize widgets (sidebar, newMsgForm, ...)
    widgets = getWidgets(request)

    context = {
        'active_page': 'profile', 'nav': Nav.nav, 'new': widgets['new'], 'msgForm': widgets['msgForm'],
        'follow_list': widgets['follow_list'],
        'hot_list': widgets['hot_list'], 'group_sb_list': widgets['group_sb_list']
    }

    if 'favorits' in request.GET or 'favorits' in request.POST:
        context['show_favs'] = True
    else:
        context['show_favs'] = False

    try:
        pUser = User.objects.get(username=user)  # this is the user displayed in html
        context['pUser'], context['pUserProf'], context['ignored'] = pUser, pUser.userprofile, False
        if request.method == 'POST' and 'ignoreUser' in request.POST:
            if 'ignoreUser' in request.POST:               # clicked User ignorieren
                ignoreUser_list = request.user.userprofile.ignoreU.all()
                if pUser in ignoreUser_list:                                # unignore(?) if user is ignored
                    request.user.userprofile.ignoreU.remove(pUser)
                    context['success_msg'] = pUser.username + " wird nicht mehr ignoriert."
                else:                                                       # ignore dat biatch
                    request.user.userprofile.ignoreU.add(pUser)
                    context['success_msg'] = pUser.username + " wird fortan ignoriert."

        elif 'delMessage' in request.POST or 'ignoreMsg' in request.POST:
            context['success_msg'] = editMessage(request)
            context['list_end'] = request.POST['list_end']

        elif request.POST and 'entfollow' in request.POST:
            entfollow = User.objects.get(id=request.POST.get('entfollow'))
            follow = Notification.objects.get(
                        Q(user__exact=entfollow) & Q(follower__exact=request.user.userprofile)
                    )
            follow.delete()
            
            context['success_msg'] = entfollow.username + " wird nicht mehr gefollowt (?) ."

        elif request.GET and 'follow' in request.GET:
            if pUser in widgets['follow_list']:
                follow = Notification.objects.get(
                    Q(user__exact=pUser) & Q(follower__exact=request.user.userprofile)
                )
                follow.delete()
                context['success_msg'] = 'Du folgst ' + user.upper() + ' jetzt nicht mehr.'
            else:
                note = request.user.username + ' folgt Dir jetzt!'
                setNotification('follower', data={'user': pUser, 'follower': request.user.userprofile, 'note': note})
                context['success_msg'] = 'Du folgst ' + user.upper() + ' jetzt.'
            widgets['follow_list'] = widgets['userProfile'].follow.all()

        if request.user.userprofile.ignoreU.filter(username=pUser.username).exists():
            context['ignored'] = True                                   # yes, so disable all messages from her profile

        if pUser in widgets['follow_list']:
            context['follow_text'] = '<span class="glyphicon glyphicon-eye-close"></span> ' + user.upper() + ' nicht folgen'
        else:
            context['follow_text'] = '<span class="glyphicon glyphicon-eye-open"></span> ' + user.upper() + ' folgen'

        # Messages
        messages = getMessages(data={'page': 'profile', 'data': pUser, 'end': end, 'request': request})
        context['message_list'], context['has_msg'] = messages['message_list'], messages['has_msg']
        if 'delMessage' or 'ignoreMsg' not in request.POST:
            context['list_end']  = messages['list_end']
    except:
        error_msg['error_no_user'] = 'Kein Benutzer mit dem Benutzernamen ' + user + ' gefunden!'
        context['error_msg'] = error_msg

    context['follow_sb_list'] = sorted(widgets['follow_list'], key=lambda x: random.random())[:5]

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
    user = User.objects.get(pk=request.user.id)
    userProfile = user.userprofile
    success_msg, error_msg, userForm, userDataForm = None, None, None, None

    # initialize widgets (sidebar, newMsgForm, ...)
    widgets = getWidgets(request)

    # check if account should be deleted
    # if true: delete account, return to FTU
    if request.method == 'POST' and request.POST['delete'] == 'true':
        userProfile.delete()
        user.delete()
        return HttpResponseRedirect('/twittur/')
    # else: validate userForm and userDataForm and save changes
    elif request.method == 'POST':
        userForm = UserForm(request.POST, instance=user)
        if userForm.is_valid():
            userDataForm = UserDataForm(request.POST, request.FILES, instance=userProfile)
            userDataForm.oldPicture = userProfile.picture
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
    userForm = UserForm(instance=user)
    userDataForm = UserDataForm(instance=userProfile)

    # return relevant information to render settings.html
    context = {
        'active_page': 'settings', 'nav': Nav.nav, 'new': widgets['new'], 'msgForm': widgets['msgForm'],
        'success_msg': success_msg, 'error_msg': error_msg,
        'user': user,
        'userForm': userForm, 'userDataForm': userDataForm
    }
    return render(request, 'settings.html', context)


def showMessage(request, msg):
    # initialize widgets (sidebar, newMsgForm, ...)
    widgets = getWidgets(request)

    context = {
        'active_page': 'message', 'nav': Nav.nav, 'new': widgets['new'], 'msgForm': widgets['msgForm'],
        'user': request.user, 'msg_id': msg,
        'hot_list': widgets['hot_list'], 'group_sb_list': widgets['group_sb_list'],
        'follow_sb_list': sorted(widgets['follow_list'], key=lambda x: random.random())[:5]
    }

    # if a message was sent to this view:
    # return success_msg
    if request.method == 'POST':
        context['success_msg'] = editMessage(request)

    # Messages
    messages = getMessages(data={'page': msg, 'data': request.user, 'request': request})
    context['message_list'], context['has_msg'] = messages['message_list'], messages['has_msg'],

    # return relevant information to render message.html
    return render(request, 'message.html', context)


def notification(request):
    # initialize widgets (sidebar, newMsgForm, ...)
    widgets = getWidgets(request)

    # for context
    ntfc_list = Notification.objects.filter(
        Q(user=request.user)
    ).order_by("-date")

    # saving boolean extra, because it will deleted by next for loop
    boolean_list = []
    for item in ntfc_list:
        if item.read == False:
            boolean_list.append('False')
        else:
            boolean_list.append('True')

    ntfc_list = zip(ntfc_list,boolean_list)

    context = {
        'active_page': 'notification', 'nav': Nav.nav, 'new': widgets['new'], 'msgForm': widgets['msgForm'],
        'user': request.user,
        'notification_list': ntfc_list,
        'hot_list': widgets['hot_list'], 'group_sb_list': widgets['group_sb_list'],
        'follow_sb_list': sorted(widgets['follow_list'], key=lambda x: random.random())[:5]
    }

    # update -> set all notification to true
    ntfc_list = Notification.objects.filter(
        Q(read=False) & Q(user=request.user)
    )
    for item in ntfc_list:
        item.read = True
        item.save()

    return render(request, 'notification.html', context)


def load_more(request):
    page = request.GET.get('page')
    end = int(request.GET.get('length')) + 5
    widgets = getWidgets(request)
    context = {'active_page': page, 'user': request.user, 'msgForm': widgets['msgForm']}

    if page == 'index':
        data = User.objects.filter(username__exact=request.user.username).select_related('userprofile')
    elif page == 'profile':
        data = User.objects.get(username=request.GET.get('user'))
        context['pUser'] = data
    elif page == 'group':
        data = GroupProfile.objects.get(short=request.GET.get('group'))
        context['group'] = data
    elif page == 'search':
        data = request.GET.get('search_input').split(" ")
        context['search_input'] = request.GET.get('search_input')
    elif page == 'hashtag':
        data = request.GET.get('hash')
        context['is_hash'] = request.GET.get('hash')

    messages = getMessages(data={'page': page, 'data': data, 'end': end, 'request': request})
    context['message_list'], context['list_end'] = messages['message_list'], messages['list_end']

    return render(request, 'message_box_reload.html', context)


def update(request):
    what = request.GET.get('what')
    if what == 'hide_msg' or what == 'hide_cmt':
        ignore_list = request.user.userprofile.ignoreM.all()
        if Message.objects.filter(pk=request.GET.get('id')).exists():
            msg = Message.objects.get(pk=request.GET.get('id'))
            if msg.user in request.user.userprofile.ignoreU.all():
                response = "<span class='glyphicon glyphicon-warning'></span>&nbsp;" \
                           "Du musst " + msg.user.username + " erst entsperren. Besuche dazu sein " \
                           "<a href='/twittur/profile/" + msg.user.username + "'>Profil</a>!"
            else:
                if msg in ignore_list:
                    request.user.userprofile.ignoreM.remove(msg)
                    response = "<span class='glyphicon glyphicon-ok'></span>&nbsp;" \
                               "Nachricht wird nicht mehr ausgeblendet!"

                else:
                    request.user.userprofile.ignoreM.add(msg)
                    response = "<span class='glyphicon glyphicon-ok'></span>&nbsp;" \
                               "Nachricht erfolgreich ausgeblendet!"
    elif what == 'del_msg' or what == 'del_cmt':
        if Message.objects.filter(comment=request.GET.get('id')).exists():
            msg = Message.objects.get(pk=request.GET.get('id'))
            comments = Message.objects.filter(comment=msg)
            for obj in comments:
                obj.delete()
        if Message.objects.filter(pk=request.GET.get('id')).exists():  # if Message exists
            curMsg = Message.objects.get(pk=request.GET.get('id'))     # select Message
            curMsg.delete()                                                 # delete selected Message
        response = "<span class='glyphicon glyphicon-ok'></span>&nbsp;" \
                   "Nachricht gel&ouml;scht!"                                   # return info

    return HttpResponse(response)