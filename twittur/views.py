"""
@package twittur
@author twittur-Team (Lilia B., Ming C., William C., Karl S., Thomas T., Steffen Z.)
Standard Views
- IndexView:            landing page for logged-in users
- LoginView:            landing page for guests
- ProfileView:          profile page for logged-in users
- ProfileSettingsView:  settings for logged-in users
- MessageView:          page to show single messages or conversations
- NotificationView:     page to show notifications
"""

import random, re

from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from .models import GroupProfile, Message, Nav, Notification, UserProfile
from .forms import UserForm, UserDataForm
from .functions import dbm_to_m, getContext, getDisciplines, getSafetyLevels, getMessages, \
    msg_to_db, setNotification, pw_generator, checkhashtag


# startpage
def IndexView(request):
    """
    view to display all messages the user is eligible to see
    :param request:
    :return: rendered HTML in template 'index.html'
    """

    if not request.user.is_authenticated():             # check if user is logged in
        return HttpResponseRedirect('/twittur/login/')  # if user is not logged in, redirect to FTU

    # context for template
    context = getContext(request, 'index', request.user)

    # if request was sent to view: return success message
    if request.method == 'POST':
        context['success_msg'] = 'Nachricht erfolgreich gesendet!'
        if 'list_end' in request.POST:
            context['list_end'] = request.POST['list_end']
    elif request.method == 'GET' and 'search_input' in request.GET:
        context['error_msg'] = {'error_search': 'Kein Suchbegriff eingegeben!'}


    # Messages
    messages = getMessages(data={'page': 'index', 'data': context['user'],
                                 'end': context['list_end'], 'request': request})

    context['list_length'], context['list_end'] = messages['list_length'], messages['list_end']
    context['has_msg'], context['message_list'] = messages['has_msg'], messages['message_list']

    return render(request, 'index.html', context)


# login/registration page
def LoginView(request):
    """

    :param request:
    :return:
    """

    # Public Messages:
    message_list = Message.objects.filter(
        Q(comment=None) & Q(attags=None) & Q(group=None)
    ).order_by('-date').distinct()

    # if user tries to log in
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

    # if user tries to register or to reset his password
    if request.method == 'POST':
        query_dict, data, error_msg, success_msg = request.POST, {}, {}, None
        username, password, email, first_name, last_name, academicDiscipline, studentNumber = \
            None, None, None, None, None, None, None

        # if user tries to reset his password, generate new one and send per mail
        # confirm user identity by checking his student number
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
                    error_msg['error_stud_number'] = "Die eingegebene Matrikel-Nummer stimmt nicht mit der " \
                                                     "Matrikel-Nummer &uuml;berein, die uns bekannt ist.<br>" \
                                                     "Wenn Du Deine eingegebe Matrikel-Nummer vergessen hast, " \
                                                     "kontaktiere ein twittur-Teammmitglied. (siehe " \
                                                     "<a href='/twittur/info'>Impressum</a>)"
            except:
                error_msg['error_not_registered'] = "Die eingegebene E-Mail Adresse ist nicht registriert."

        # if a guest wants to register
        else:
            userList, username = User.objects.all(), query_dict.get('name')

            # case if username is available
            for user in userList:
                if username.lower() == user.username.lower():
                    error_msg['error_reg_user_n'] = "Sorry, Username ist vergeben."
            if 'error_reg_user_n' not in error_msg:
                if re.match("^[a-zA-Z0-9-_.]*$", username):
                    data['username'] = username
                else:
                    error_msg['error_reg_user_n'] = "Nur 'A-Z, a-z, 0-9, -, _' und '.' im Usernamen erlaubt!"

            # Password validation
            password = query_dict.get('password')
            ack_password = query_dict.get('ack_password')
            if password != ack_password:
                error_msg['error_reg_user_p'] = "Passw&ouml;rter sind nicht gleich."

            # EMail validation
            email = query_dict.get('email')
            mail = email.split('@')
            if len(mail) == 1 or not (
                mail[1].endswith(".tu-berlin.de") or (email[(len(email) - 13):len(email)] == '@tu-berlin.de')):
                error_msg['error_reg_mail'] = "Keine g&uuml;tige TU E-Mail Adresse!"
            else:
                try:
                    User.objects.get(email=email)
                    error_msg['error_reg_mail'] = "Ein Benutzer mit dieser E-Mail Adresse existiert bereits!"
                except:
                    data['email'] = email

            # fill the rest for model User and Userprofile
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
                    error_msg["error_student_number"] = "Ein Benutzer mit dieser Matrikel-Nummer existiert bereits."
                except:
                    data['studentNumber'] = studentNumber
            else:
                error_msg['error_student_number'] = "Die eingegebene Matrikel-Nummer ist ung&uuml;ltig!"
            academicDiscipline = query_dict.get('academicDiscipline')
            if len(academicDiscipline) > 0:
                data['academicDiscipline'] = academicDiscipline
            else:
                error_msg['error_reg_userprofile_ad'] = "Bitte Studiengang ausw&auml;hlen!"

        # context for html
        context = {
            'active_page': 'ftu',
            'nav': Nav.nav,
            'data': data,
            'errors': error_msg,
            'message_list': message_list
        }

        # error?
        if len(error_msg) > 0 or 'password_reset' in request.POST:
            if 'password_reset' in request.POST:
                context['pActive'] = 'active'
                if success_msg: context['success_msg'] = success_msg
            else:
                context['rActive'] = 'active'

            return render(request, 'ftu.html', context)

        # if data is correct -> create User and Userprofile
        user = User.objects.create_user(username, email, password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        userProfile = UserProfile(userprofile=user, studentNumber=studentNumber,
                                  academicDiscipline=academicDiscipline, location="Irgendwo")
        userProfile.save()

        # academic discipline (required user in db)
        # -> add user to group uni, fac whatever and his academic discipline
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

    context = {
        'active_page': 'ftu',
        'nav': Nav.nav,
        'message_list': message_list,
        'discList': getDisciplines()
    }
    return render(request, 'ftu.html', context)


# logout
def logout(request):
    """
    method to end logged-in users session
    :param request:
    :return: redirect to index (landing-page)
    """

    auth.logout(request)
    return HttpResponseRedirect('/twittur/')


# Page: 'Profilseite'
def ProfileView(request, user):
    """
    view to display specific users information
    :param request:
    :param user: username of user to be displayed
    :return: rendered HTML in template 'profile.html'
    """

    if not request.user.is_authenticated():             # check if user is logged in
        return HttpResponseRedirect('/twittur/login/')  # if user is not logged in, redirect to FTU

    # context for template
    context = getContext(request, 'profile', user)

    # GET request "Alle anzeigen" for group or favorites
    if 'favorits' in request.GET or 'favorits' in request.POST:
        context['show_favs'] = True
    elif 'group' in request.GET or 'group' in request.POST:
        context['show_groups'] = True

    try:
        user = user.lower()
        pUser = User.objects.get(username=user)  # this is the user displayed in html
        context['pUser'], context['pUserProf'] = pUser, pUser.userprofile
        if request.method == 'POST':
            dict = request.POST
            if 'ignoreUser' in dict: # clicked User ignorieren
                ignoreUser_list = context['userProfile'].ignoreU.all()
                if pUser in ignoreUser_list:                                # unignore(?) if user is ignored
                    context['userProfile'].ignoreU.remove(pUser)
                    context['success_msg'] = pUser.username + " wird nicht mehr ignoriert."
                else:                                                       # ignore dat biatch
                    context['userProfile'].ignoreU.add(pUser)
                    context['success_msg'] = pUser.username + " wird fortan ignoriert."

            elif 'entfollow' in dict:
                entfollow = User.objects.get(id=dict['entfollow'])
                follow = Notification.objects.get(
                            Q(user__exact=entfollow) & Q(follower__exact=context['userProfile'])
                        )
                follow.delete()
                context['success_msg'] = entfollow.username + " wird nicht mehr gefollowt (?) ."

            elif 'leaveGroup' in dict:
                group = GroupProfile.objects.get(id = dict['leaveGroup'])
                # g = Notification.objects.get( Q(user_exact=request.user) & Q(group=group))
                group.member.remove(request.user)
                note = request.user.username + ' hat deine Gruppe verlassen.'
                setNotification('group', data={'group': group, 'member': group.admin, 'note': note})
                context['success_msg'] = 'Ihr habt die Gruppe "' + group.name + '" verlassen.'

        elif 'follow' in request.GET:
            if pUser in context['follow_list']:
                follow = Notification.objects.get(
                    Q(user__exact=pUser) & Q(follower__exact=context['userProfile'])
                )
                follow.delete()
                context['success_msg'] = 'Du folgst ' + user.upper() + ' jetzt nicht mehr.'
            else:
                note = request.user.username + ' folgt Dir jetzt!'
                setNotification('follower', data={'user': pUser, 'follower': context['userProfile'], 'note': note})
                context['success_msg'] = 'Du folgst ' + user.upper() + ' jetzt.'

        context['follow_list'] = context['userProfile'].follow.all()

        if context['userProfile'].ignoreU.filter(username=pUser.username).exists():
            context['ignored'] = True                                   # yes, so disable all messages from her profile

        if pUser in context['follow_list']:
            context['follow_text'] = '<span class="glyphicon glyphicon-eye-close"></span> ' + user.upper() + ' nicht folgen'
        else:
            context['follow_text'] = '<span class="glyphicon glyphicon-eye-open"></span> ' + user.upper() + ' folgen'

        # Messages
        messages = getMessages(data={'page': 'profile', 'data': pUser, 'end': 5, 'request': request})

        context['list_length'], context['list_end'] = messages['list_length'], messages['list_end']
        context['has_msg'], context['message_list'] = messages['has_msg'], messages['message_list']

        if 'delMessage' or 'ignoreMsg' not in request.POST:
            context['list_end']  = messages['list_end']
    except:
        context['error_msg']['error_no_user'] = 'Kein Benutzer mit dem Benutzernamen ' + user + ' gefunden!'

    context['follow_sb_list'] = sorted(context['follow_list'], key=lambda x: random.random())[:5]

    return render(request, 'profile.html', context)


# Page: 'Einstellungen'
def ProfileSettingsView(request):
    """
    view to update account and personal information
    -- picture, email, password, first_name, last_name,
       academicDiscipline, studentNumber, location
    user can also delete its account
    :param request:
    :return: rendered HTML in template 'settings.html'
    """

    if not request.user.is_authenticated():             # check if user is logged in
        return HttpResponseRedirect('/twittur/login/')  # if user is not logged in, redirect to FTU

    context = getContext(request, page='settings', user=request.user)

    # get current users information and initialize return messages
    user = User.objects.get(pk=request.user.id)
    userProfile = user.userprofile
    userGroup = GroupProfile.objects.get(name=userProfile.academicDiscipline)

    # check if account should be deleted
    # if true: delete account, return to FTU
    if request.method == 'POST':
        dict = request.POST
        if dict['delete'] == 'true':
            userProfile.delete()
            user.delete()
            return HttpResponseRedirect('/twittur/')
        # else: validate userForm and userDataForm and save changes
        else:
            userForm = UserForm(dict, instance=user)
            if userForm.is_valid():
                userDataForm = UserDataForm(dict, request.FILES, instance=userProfile)
                userDataForm.oldPicture = userProfile.picture

                # if picture has changed, delete old picture
                # do not, if old picture was default picture
                if 'picture' in request.FILES or 'picture-clear' in dict:
                    if userDataForm.oldPicture != 'picture/default.gif':
                        userDataForm.oldPicture.delete()
                if userDataForm.is_valid():
                     # safety change
                    safety = userDataForm.instance.safety
                    if safety.lower() != dict['safety'].lower():
                        userDataForm.instance.safety = dict['safety']
                    else:
                        pass
                    userForm.save()
                    userDataForm.save()

                    # re-authenticate user if he changed his password
                    if 'password' in dict and len(dict['password']) > 0:
                        username = dict['username']
                        password = dict['password']
                        user = authenticate(username=username, password=password)
                        auth.login(request, user)

                    context['success_msg'] = 'Benutzerdaten wurden erfolgreich aktualisiert.'
                else:
                    # return errors if userDataForm is not valid
                    context['error_msg'] = userDataForm.errors
            else:
                # return errors if userForm is not valid
                context['error_msg'] = userForm.errors

            # academic discipline (required user in db)
            # -> add user to group uni, fac whatever and his academic discipline
            try:
                group = GroupProfile.objects.get(name=userProfile.academicDiscipline)
                group_list = GroupProfile.objects.filter(Q(member__exact=request.user))
                if group is not userGroup:
                    if user in userGroup.member.all():
                        userGroup.member.remove(user)
                if user not in group.member.all():
                    while True:
                        if group.supergroup == None:
                            if user not in group.member.all():
                                group.member.add(user)
                            break
                        else:
                            if group != userGroup.supergroup and group.supergroup.short == 'uni':
                                userSuperGroup = userGroup.supergroup
                                userSuperGroup.member.remove(user)
                            if user not in group.member.all():
                                group.member.add(user)
                            group = group.supergroup
            except:
                print("error, something went wrong")
                pass

    # update current users information if changed
    if request.method == 'POST':
        user = User.objects.get(pk=request.user.id)
        userProfile = user.userprofile
        context['user'], context['userProfile'] = user, userProfile

    # initialize UserForm and UserDataForm with current users information
    context['userForm'], context['userDataForm'] = UserForm(instance=user), UserDataForm(instance=userProfile)
    context['discList'], context['safetyLevelList'] = getDisciplines(), getSafetyLevels(user)

    return render(request, 'settings.html', context)


def MessageView(request, msg):
    """
    view to show messages / conversations
    :param request:
    :param msg: ID of displayed message
    :return: rendered HTML in template 'message.html'
    """

    if not request.user.is_authenticated():             # check if user is logged in
        return HttpResponseRedirect('/twittur/login/')  # if user is not logged in, redirect to FTU

    # initialize data dictionary 'context' with relevant display information
    context = getContext(request, page='message', user=request.user)
    context['msg_id'] = msg

    # if a message was sent to this view:
    # return success_msg
    if request.method == 'POST':
        context['success_msg'] = 'Nachricht erfolgreich gesendet!'

    # gets all Messages
    messages = getMessages(data={'page': msg, 'data': request.user, 'request': request})
    context['message_list'], context['has_msg'] = messages['message_list'], messages['has_msg'],

    # return relevant information to render message.html
    return render(request, 'message.html', context)


def NotificationView(request):
    """
    view that shows notifications
    after getting the notification list, all notifications will be marked as read
    :param request:
    :return: rendered HTML in template 'notification.html'
    """

    if not request.user.is_authenticated():             # check if user is logged in
        return HttpResponseRedirect('/twittur/login/')  # if user is not logged in, redirect to FTU

    # initialize data dictionary 'context' with relevant display information
    context = getContext(request, page='notification', user=request.user)
    context['ntfc_list'] = Notification.objects.filter(Q(user=request.user)).order_by("-date").distinct()

    # saving boolean extra, because it will deleted by next for loop
    boolean_list = []
    for item in context['ntfc_list']:
        if item.read == False: boolean_list.append('False')
        else: boolean_list.append('True')

    context['ntfc_list'] = zip(context['ntfc_list'], boolean_list)

    # update -> set all notification to true
    ntfc_list = Notification.objects.filter(Q(read=False) & Q(user=request.user))
    for item in ntfc_list:
        item.read = True
        item.save()

    return render(request, 'notification.html', context)


def load_more(request):
    """
    loads further messages to current view
    :param request:
    :return: rendered HTML in Template 'message_box_reload.html'
    """

    if not request.user.is_authenticated():             # check if user is logged in
        return HttpResponseRedirect('/twittur/login/')  # if user is not logged in, redirect to FTU

    dict = request.GET
    page = dict.get('page')

    # initialize data dictionary 'context' with relevant display information
    context = getContext(request, page=page, user=request.user)

    # gets specific data to display new messages for different pages
    # cases: 'index, profile, group, search, hashtag'
    if page == 'index':
        data = request.user
    elif page == 'profile':
        data = User.objects.get(username=dict['user'])
        context['pUser'] = data
    elif page == 'group':
        data = GroupProfile.objects.get(short=dict['group'])
        context['group'] = data
    elif page == 'search':
        data = dict['search_input'].split(" ")
        context['search_input'] = dict['search_input']
    elif page == 'hashtag':
        data = dict.get('hash')
        context['is_hash'] = dict['hash']

    messages = getMessages(data={'page': page, 'data': data,
                                 'end': (int(dict['length'])+5), 'request': request})

    context['list_length'], context['list_end'] = messages['list_length'], messages['list_end']
    context['has_msg'], context['message_list'] = messages['has_msg'], messages['message_list']

    if 'new_msgs' in messages:
        context['new_msgs'] = messages['new_msgs']

    return render(request, 'message_box_reload.html', context)


def update(request):
    """
    processes request to update a message / comment
    - 'hide_msg', 'hide_cmt':   puts message / comment on message-ignore-list
    - 'del_msg', 'del_cmt':     deletes message / comments and its comments, as well as its picture from the database
    - 'upd_msg':                updates a message / comment with current information
    :param request:
    :return: String with update status
    """

    if not request.user.is_authenticated():             # check if user is logged in
        return HttpResponseRedirect('/twittur/login/')  # if user is not logged in, redirect to FTU

    dict = request.GET

    # message / comment will be added to user's message-ignore-list
    if dict['what'] in ('hide_msg', 'hide_cmt'):
        userProfile = request.user.userprofile
        ignore_list = userProfile.ignoreM.all()
        if Message.objects.filter(pk=dict['id']).exists():
            msg = Message.objects.get(pk=dict['id'])
            if msg.user in userProfile.ignoreU.all():
                response = "<span class='glyphicon glyphicon-warning'></span>&nbsp;" \
                           "Du musst " + msg.user.username + " erst entsperren. Besuche dazu sein " \
                           "<a href='/twittur/profile/" + msg.user.username + "'>Profil</a>!"
            else:
                if msg in ignore_list:
                    userProfile.ignoreM.remove(msg)
                    response = "<span class='glyphicon glyphicon-ok'></span>&nbsp;" \
                               "Nachricht wird nicht mehr ausgeblendet!"

                else:
                    userProfile.ignoreM.add(msg)
                    response = "<span class='glyphicon glyphicon-ok'></span>&nbsp;" \
                               "Nachricht erfolgreich ausgeblendet!"

    # message / comment and its data (comments, hashtag) will be delete from the database
    elif dict['what'] in ('del_msg', 'del_cmt'):
        if Message.objects.filter(pk=dict['id']).exists():
            msg = Message.objects.get(pk=dict['id'])
            if Message.objects.filter(comment=dict['id']).exists():
                comments = Message.objects.filter(comment=msg)
                for obj in comments:
                    hashtaglist = []
                    for hashtag in obj.hashtags.all():
                        hashtaglist.append(hashtag)
                    if hashtaglist:
                        checkhashtag(obj, hashtaglist)
                    obj.delete()
            if msg.picture:
                pic = msg.picture
                pic.delete()
            hashtaglist = []
            for hashtag in msg.hashtags.all():
                hashtaglist.append(hashtag)
            if hashtaglist:
                checkhashtag(msg, hashtaglist)
            msg.delete()
        response = "<span class='glyphicon glyphicon-ok'></span>&nbsp;" \
                   "Nachricht gel&ouml;scht!"

    # message will be updated with current information.
    # may clear the picture and delete it from its folder
    # may change safetyLevel
    elif dict['what'] == 'upd_msg':
        if Message.objects.filter(pk=dict['id']).exists():
            msg = Message.objects.get(pk=dict['id'])
            msg.text = dict['val']
            if 'clear' in dict and dict['clear'] == 'true':
                if msg.picture is not None:
                    pic = msg.picture
                    pic.delete()
                    msg.picture = None
            if 'safety' in dict:
                if dict['safety'][:1] == '&':
                    group = GroupProfile.objects.get(short__exact=dict['safety'][1:])
                elif dict['safety'] == 'Public':
                    group = None
                else:
                    group = GroupProfile.objects.get(name__exact=dict['safety'])
                msg.group = group
            msg.save()
            msg_to_db(msg)
            response = dbm_to_m(msg).text
    else:
        response = "Something went wrong."

    return HttpResponse(response)


def vierNullVier(request):
    """

    :param request:
    :return:
    """

    if not request.user.is_authenticated():             # check if user is logged in
        return HttpResponseRedirect('/twittur/login/')  # if user is not logged in, redirect to FTU

    # initialize data dictionary 'context' with relevant display information
    context = getContext(request, '404', user=request.user)

    return render(request, '404.html', context)