"""
-*- coding: utf-8 -*-
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

import random
import re

from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse

from .models import GroupProfile, Hashtag, Message, Nav, Notification, UserProfile
from .forms import UserForm, UserDataForm
from .functions import get_context, get_disciplines, get_messages, get_safety_levels, pw_generator, set_notification, \
    verification_mail


# Page: "Startseite"
def index_view(request):
    """
    view to display all messages the user is eligible to see
    :param request:
    :return: rendered HTML in template 'index.html'
    """

    if not request.user.is_authenticated():             # check if user is logged in
        return HttpResponseRedirect('/twittur/login/')  # if not -> redirect to FTU

    # initialize data dictionary 'context' with relevant display information
    context = get_context(request, 'index', request.user)

    # if request was sent to view: return success message
    if request.method == 'POST':
        context['success_msg'] = 'Nachricht erfolgreich gesendet!'
        if 'list_end' in request.POST:
            context['list_end'] = request.POST['list_end']
    elif request.method == 'GET' and 'search_input' in request.GET:
        context['error_msg'] = {'error_search': 'Kein Suchbegriff eingegeben!'}

    # Messages
    messages = get_messages(data={'page': 'index', 'data': context['user'],
                                  'end': context['list_end'], 'request': request})

    context['list_length'], context['list_end'] = messages['list_length'], messages['list_end']
    context['has_msg'], context['message_list'] = messages['has_msg'], messages['message_list']

    return render(request, 'index.html', context)


# Page: "Startseite (not logged in)"
def login_view(request):
    """

    :param request:
    :return: rendered HTML in template 'ftu.html'
    """

    # Public Messages:
    message_list = Message.objects.filter(Q(comment=None) & Q(attags=None) & Q(group=None)).order_by('-date')
    hashtag_list = Hashtag.objects.annotate(hashtag_count=Count('hashtags__hashtags__name')).order_by('-hashtag_count')
    context = {'active_page': 'ftu',
               'message_list': message_list, 'hashtag_list': hashtag_list, 'discList': get_disciplines()}

    # if user tries to log in
    if request.method == "GET":
        if 'login' in request.GET:
            username, password = request.GET.get('username'), request.GET.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    return HttpResponseRedirect('/twittur/')
                else:
                    context['error_login'] = "Dein Account wurde noch nicht verifiziert!"
            else:
                context['error_login'] = "Ups, Username oder Passwort falsch."
            return render(request, 'ftu.html', context)

    # if user tries to register or to reset his password
    if request.method == 'POST':
        query_dict, data, error_msg, success_msg = request.POST, {}, {}, None
        username, password, email, first_name, last_name, academic_discipline, student_number = \
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
            except ObjectDoesNotExist as e:
                print(e)
                error_msg['error_not_registered'] = "Die eingegebene E-Mail Adresse ist nicht registriert."

        # if a guest wants to register
        else:
            user_list, username = User.objects.all(), query_dict['name']

            # case if username is available
            for user in user_list:
                if username.lower() == user.username.lower():
                    error_msg['error_reg_user_n'] = "Sorry, Username ist vergeben."
            if 'error_reg_user_n' not in error_msg:
                if re.match("^[a-zA-Z0-9-_.]*$", username):
                    data['username'] = username
                else:
                    error_msg['error_reg_user_n'] = "Nur 'A-Z, a-z, 0-9, -, _' und '.' im Usernamen erlaubt!"

            # Password validation
            password, ack_password = query_dict['password'], query_dict['ack_password']
            if password != ack_password:
                error_msg['error_reg_user_p'] = "Passw&ouml;rter sind nicht gleich."

            # EMail validation
            email = query_dict['email']
            mail = email.split('@')
            if len(mail) == 1 or not (mail[1].endswith(".tu-berlin.de")
                                      or (email[(len(email) - 13):len(email)] == '@tu-berlin.de')):
                error_msg['error_reg_mail'] = "Keine g&uuml;ltige TU E-Mail Adresse!"
            else:
                try:
                    User.objects.get(email=email)
                    error_msg['error_reg_mail'] = "Ein Benutzer mit dieser E-Mail Adresse existiert bereits!"
                except ObjectDoesNotExist as e:
                    print(e)
                    data['email'] = email

            # fill the rest for model User and Userprofile
            first_name, last_name = query_dict['first_name'], query_dict['last_name']
            academic_discipline = query_dict['academicDiscipline']
            if len(first_name) > 0:
                data['first_name'] = first_name
            if len(last_name) > 0:
                data['last_name'] = last_name
            if len(query_dict['studentNumber']) == 6:
                student_number = query_dict['studentNumber']
                try:
                    UserProfile.objects.get(studentNumber=student_number)
                    error_msg["error_student_number"] = "Ein Benutzer mit dieser Matrikel-Nummer existiert bereits."
                except ObjectDoesNotExist as e:
                    print(e)
                    data['studentNumber'] = student_number
            else:
                error_msg['error_student_number'] = "Die eingegebene Matrikel-Nummer ist ung&uuml;ltig!"
            if len(academic_discipline) > 0:
                data['academicDiscipline'] = academic_discipline
            else:
                error_msg['error_reg_userprofile_ad'] = "Bitte Studiengang ausw&auml;hlen!"

        # context for html
        context['data'], context['errors'] = data, error_msg

        # error?
        if len(error_msg) > 0 or 'password_reset' in request.POST:
            if 'password_reset' in request.POST:
                context['pActive'] = 'active'
                if success_msg:
                    context['success_msg'] = success_msg
            else:
                context['rActive'] = 'active'

            return render(request, 'ftu.html', context)

        # if data is correct -> create User and Userprofile
        user = User.objects.create_user(username, email, password)
        user.first_name, user.last_name, user.is_active = first_name, last_name, False
        user.save()

        # Hash for verification
        new_hash = pw_generator()
        user_profile = UserProfile(userprofile=user, studentNumber=student_number,
                                   academicDiscipline=academic_discipline, location="Irgendwo",
                                   verifyHash=new_hash)
        user_profile.save()
        verification_mail(user, request)

        # academic discipline (required user in db)
        # -> add user to group uni, fac whatever and his academic discipline
        try:
            group = GroupProfile.objects.get(name=academic_discipline)
            while True:
                group.member.add(user)
                if group.supergroup is None:
                    break
                else:
                    group = group.supergroup

        except ObjectDoesNotExist as e:
            print(e)
            pass

        location = reverse("twittur:pleaseVerify")
        return HttpResponseRedirect(location)

    return render(request, 'ftu.html', context)


# Page: "Profilseite"
def profile_view(request, user):
    """
    view to display specific users information
    :param request:
    :param user: username of user to be displayed
    :return: rendered HTML in template 'profile.html'
    """

    if not request.user.is_authenticated():             # check if user is logged in
        return HttpResponseRedirect('/twittur/login/')  # if user is not logged in, redirect to FTU

    # initialize data dictionary 'context' with relevant display information
    context = get_context(request, 'profile', user)

    # GET request "Alle anzeigen" for group or favorites
    if 'favorits' in request.GET or 'favorits' in request.POST:
        context['show_favs'] = True
    elif 'group' in request.GET or 'group' in request.POST:
        context['show_groups'] = True

    try:
        p_user = User.objects.get(username=user.lower())  # this is the user displayed in html
        context['pUser'], context['pUserProf'] = p_user, p_user.userprofile
        data_dict = None
        if request.method == 'POST':
            data_dict = request.POST
        elif request.method == 'GET':
            data_dict = request.GET

        if 'ignoreUser' in data_dict:                                     # clicked User ignorieren
            ignore_user_list = context['userProfile'].ignoreU.all()
            if p_user in ignore_user_list:                                # unignore(?) if user is ignored
                context['userProfile'].ignoreU.remove(p_user)
                context['success_msg'] = p_user.username + " wird nicht mehr ignoriert."
            else:                                                       # ignore dat biatch
                context['userProfile'].ignoreU.add(p_user)
                context['success_msg'] = p_user.username + " wird fortan ignoriert."

        if 'follow' in request.GET:
            if p_user in context['follow_list']:
                follow = Notification.objects.get(Q(user__exact=p_user) & Q(follower__exact=context['userProfile']))
                follow.delete()
                context['success_msg'] = 'Du folgst ' + user.upper() + ' jetzt nicht mehr.'
            else:
                note = request.user.username + ' folgt Dir jetzt!'
                set_notification('follower', data={'user': p_user, 'follower': context['userProfile'], 'note': note})
                context['success_msg'] = 'Du folgst ' + user.upper() + ' jetzt.'

        elif 'entfollow' in data_dict:
            entfollow = User.objects.get(id=data_dict['entfollow'])
            follow = Notification.objects.get(Q(user__exact=entfollow) & Q(follower__exact=context['userProfile']))
            follow.delete()
            context['success_msg'] = entfollow.username + " wird nicht mehr gefollowt (?) ."

        elif 'leaveGroup' in data_dict:
            group = GroupProfile.objects.get(id=data_dict['leaveGroup'])
            group.member.remove(request.user)
            note = request.user.username + ' hat deine Gruppe verlassen.'
            set_notification('group', data={'group': group, 'member': group.admin, 'note': note})
            context['success_msg'] = 'Ihr habt die Gruppe "' + group.name + '" verlassen.'

        context['follow_list'] = context['userProfile'].follow.all()

        if context['userProfile'].ignoreU.filter(username=p_user.username).exists():
            context['ignored'] = True                                   # yes, so disable all messages from her profile

        if p_user in context['follow_list']:
            context['follow_text'] = '<span class="glyphicon glyphicon-eye-close"></span> '\
                                     + user.upper() + ' nicht folgen'
        else:
            context['follow_text'] = '<span class="glyphicon glyphicon-eye-open"></span> ' + user.upper() + ' folgen'

        # Messages
        messages = get_messages(data={'page': 'profile', 'data': p_user, 'end': 5, 'request': request})

        context['list_length'], context['list_end'] = messages['list_length'], messages['list_end']
        context['has_msg'], context['message_list'] = messages['has_msg'], messages['message_list']

        if 'delMessage' or 'ignoreMsg' not in request.POST:
            context['list_end'] = messages['list_end']
    except ObjectDoesNotExist as e:
        print(e)
        context['error_msg']['error_no_user'] = 'Kein Benutzer mit dem Benutzernamen ' + user + ' gefunden!'

    context['follow_sb_list'] = sorted(context['follow_list'], key=lambda x: random.random())[:5]

    return render(request, 'profile.html', context)


# Page: "Einstellungen"
def profile_settings_view(request):
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

    # initialize data dictionary 'context' with relevant display information
    context = get_context(request, page='settings', user=request.user)

    # get current users information and initialize return messages
    user = User.objects.get(pk=request.user.id)
    user_profile = user.userprofile
    user_group = GroupProfile.objects.get(name=user_profile.academicDiscipline)

    # check if account should be deleted
    # if true: delete account, return to FTU
    if request.method == 'POST':
        data_dict = request.POST
        if data_dict['delete'] == 'true':
            user_profile.delete()
            user.delete()
            return HttpResponseRedirect('/twittur/')
        # else: validate userForm and userDataForm and save changes
        else:
            user_form = UserForm(data_dict, instance=user)
            if user_form.is_valid():
                user_data_form = UserDataForm(data_dict, request.FILES, instance=user_profile)
                user_data_form.oldPicture = user_profile.picture

                # if picture has changed, delete old picture
                # do not, if old picture was default picture
                if 'picture' in request.FILES or 'picture-clear' in data_dict:
                    if user_data_form.oldPicture != 'picture/default.gif':
                        user_data_form.oldPicture.delete()
                if user_data_form.is_valid():
                    safety = user_data_form.instance.safety                     # safety change
                    if safety.lower() != data_dict['safety'].lower():
                        user_data_form.instance.safety = data_dict['safety']
                    else:
                        pass
                    user_form.save()
                    user_data_form.save()

                    # re-authenticate user if he changed his password
                    if 'password' in data_dict and len(data_dict['password']) > 0:
                        username = data_dict['username']
                        password = data_dict['password']
                        user = authenticate(username=username, password=password)
                        auth.login(request, user)

                    context['success_msg'] = 'Benutzerdaten wurden erfolgreich aktualisiert.'
                else:
                    # return errors if userDataForm is not valid
                    context['error_msg'] = user_data_form.errors
            else:
                # return errors if userForm is not valid
                context['error_msg'] = user_form.errors

            # academic discipline (required user in db)
            # -> add user to group uni, fac whatever and his academic discipline
            try:
                group = GroupProfile.objects.get(name=user_profile.academicDiscipline)
                if group is not user_group:
                    if user in user_group.member.all():
                        user_group.member.remove(user)
                if user not in group.member.all():
                    while True:
                        if group.supergroup is None:
                            if user not in group.member.all():
                                group.member.add(user)
                            break
                        else:
                            if group != user_group.supergroup and group.supergroup.short == 'uni':
                                user_super_group = user_group.supergroup
                                user_super_group.member.remove(user)
                            if user not in group.member.all():
                                group.member.add(user)
                            group = group.supergroup
            except ObjectDoesNotExist as e:
                print(e.__traceback__)
                pass

    # update current users information if changed
    if request.method == 'POST':
        user = User.objects.get(pk=request.user.id)
        user_profile = user.userprofile
        context['user'], context['userProfile'] = user, user_profile

    # initialize UserForm and UserDataForm with current users information
    context['userForm'], context['userDataForm'] = UserForm(instance=user), UserDataForm(instance=user_profile)
    context['discList'], context['safetyLevelList'] = get_disciplines(), get_safety_levels(user)

    return render(request, 'settings.html', context)


# Page: "Nachricht / Konversation"
def message_view(request, msg):
    """
    view to show messages / conversations
    :param request:
    :param msg: ID of displayed message
    :return: rendered HTML in template 'message.html'
    """

    if not request.user.is_authenticated():             # check if user is logged in
        return HttpResponseRedirect('/twittur/login/')  # if user is not logged in, redirect to FTU

    # initialize data dictionary 'context' with relevant display information
    context = get_context(request, page='message', user=request.user)
    context['msg_id'] = msg

    # if a message was sent to this view:
    # return success_msg
    if request.method == 'POST':
        context['success_msg'] = 'Nachricht erfolgreich gesendet!'

    # gets all Messages
    messages = get_messages(data={'page': msg, 'data': request.user, 'request': request})
    context['message_list'], context['has_msg'] = messages['message_list'], messages['has_msg'],

    # return relevant information to render message.html
    return render(request, 'message.html', context)


# Page: "Benachrichtigungen"
def notification_view(request):
    """
    view that shows notifications
    after getting the notification list, all notifications will be marked as read
    :param request:
    :return: rendered HTML in template 'notification.html'
    """

    if not request.user.is_authenticated():             # check if user is logged in
        return HttpResponseRedirect('/twittur/login/')  # if user is not logged in, redirect to FTU

    # initialize data dictionary 'context' with relevant display information
    context = get_context(request, page='notification', user=request.user)
    context['ntfc_list'] = Notification.objects.filter(Q(user=request.user)).order_by("-date").distinct()

    # saving boolean extra, because it will deleted by next for loop
    boolean_list = []
    for item in context['ntfc_list']:
        if not item.read:
            boolean_list.append('False')
        else:
            boolean_list.append('True')

    context['ntfc_list'] = zip(context['ntfc_list'], boolean_list)

    # update -> set all notification to true
    ntfc_list = Notification.objects.filter(Q(read=False) & Q(user=request.user))
    for item in ntfc_list:
        item.read = True
        item.save()

    return render(request, 'notification.html', context)


# Page: "404-Fehler"
def vier_null_vier(request):
    """

    :param request:
    :return:
    """

    if not request.user.is_authenticated():             # check if user is logged in
        return HttpResponseRedirect('/twittur/login/')  # if user is not logged in, redirect to FTU

    # initialize data dictionary 'context' with relevant display information
    context = get_context(request, '404', user=request.user)

    return render(request, '404.html', context)


def please_verify_view(request):
    return render(request, 'pleaseVerify.html', {'active_page': 'pleaseVerify'})
