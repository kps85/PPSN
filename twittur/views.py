# -*- coding: utf-8 -*-
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


import re

from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .models import GroupProfile, Hashtag, Message, Notification, UserProfile
from .forms import UserForm, UserDataForm
from .functions import create_abs_url, get_context, get_disciplines, get_messages, get_safety_levels, pw_generator, set_notification, \
    verification_mail


# Page: "Startseite"
def index_view(request):
    """
    view to display all messages the user is eligible to see
    :param request:
    :return: rendered HTML in template 'index.html'
    """

    if len(User.objects.all()) == 0:
        return HttpResponseRedirect(reverse("twittur:install"))

    if not request.user.is_authenticated():             # check if user is logged in
        return HttpResponseRedirect(reverse("twittur:login"))  # if not -> redirect to FTU

    # initialize data dictionary 'context' with relevant display information
    context = get_context(request, 'index', request.user)

    # if request was sent to view: return success message
    if request.method == 'POST':
        context['success_msg'] = 'Nachricht erfolgreich gesendet!'
        if 'list_end' in request.POST:
            context['list_end'] = request.POST['list_end']
    elif request.method == 'GET' and 'search_input' in request.GET:
        context['error_msg'] = {'error_search': 'Geben Sie einen Suchbegriff ein!'}

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
    :return: rendered HTML in template 'index_ftu.html'
    """

    # Public Messages:
    message_list = Message.objects.filter(Q(comment=None) & Q(attags=None) & Q(group=None)).order_by('-date')
    hashtag_list = Hashtag.objects.annotate(hashtag_count=Count('hashtags__hashtags__name')).order_by('-hashtag_count')
    context = {'active_page': 'ftu',
               'message_list': message_list[:10], 'hashtag_list': hashtag_list, 'discList': get_disciplines()}

    # if user tries to log in
    if request.method == "GET":
        if 'login' in request.GET:
            username, password = request.GET['username'].lower(), request.GET['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    return HttpResponseRedirect(reverse("twittur:index"))
                else:
                    context['error_login'] = "Ihr Account wurde noch nicht verifiziert!"
            else:
                context['error_login'] = "Ups, Username oder Passwort falsch."
            return render(request, 'index_ftu.html', context)

    # if user tries to register or to reset his password
    if request.method == 'POST':
        query_dict, data, error_msg, success_msg = request.POST, {}, {}, None
        username, password, email, first_name, last_name, academic_discipline = \
            None, None, None, None, None, None

        # if user tries to reset his password, generate new one and send per mail
        # confirm user identity by checking his verify hash
        if 'password_reset' in request.POST:
            if User.objects.filter(email=request.POST['pw_reset_mail']).exists():
                user = User.objects.get(email=request.POST['pw_reset_mail'])
                message = "Hallo!\n" \
                          "\n" \
                          "Sie haben ein neues Passwort fuer Ihren Account bei twittur beantragt.\n" \
                          "\n" \
                          "Bitte besuchen Sie folgenden Link um Ihr Passwort zu aendern:\n" \
                          + create_abs_url(request, 'reset_pw', data={'username': user.username,
                                                                      'hash_item': user.userprofile.verifyHash}) + \
                          "\n\n" \
                          "Wir freuen uns auf Ihren Besuch!\n" \
                          "\n" \
                          "Mit freundlichen Gruessen,\n" \
                          "Ihr twittur Team!"
                send_mail("Neues Passwort beantragt", message, "twittur.sn@gmail.com",
                          [request.POST['pw_reset_mail']])
                user.set_password(password)
                user.save()
                success_msg = 'Pr&uuml;fen Sie Ihre E-Mails!'
            else:
                error_msg['error_not_registered'] = "Die eingegebene E-Mail Adresse ist nicht registriert."

        # if a guest wants to register
        else:
            user_list, username = User.objects.all(), query_dict['name'].lower()

            # case if username is available
            for user in user_list:
                if username == user.username.lower():
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
                if User.objects.filter(email=email).exists():
                    error_msg['error_reg_mail'] = "Ein Benutzer mit dieser E-Mail Adresse existiert bereits!"
                else:
                    data['email'] = email

            # fill the rest for model User and Userprofile
            first_name, last_name = query_dict['first_name'], query_dict['last_name']
            academic_discipline = query_dict['academicDiscipline']
            if len(first_name) > 0:
                data['first_name'] = first_name
            if len(last_name) > 0:
                data['last_name'] = last_name
            if len(academic_discipline) > 0:
                data['academicDiscipline'] = academic_discipline
            else:
                error_msg['error_reg_userprofile_ad'] = "Bitte w&auml;hlen Sie einen Studiengang aus!"

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

            return render(request, 'index_ftu.html', context)

        # if data is correct -> create User and Userprofile
        user = User.objects.create_user(username, email, password)
        user.first_name, user.last_name, user.is_active = first_name, last_name, False

        # Hash for verification
        new_hash = pw_generator(hashed=True)
        user_profile = UserProfile(userprofile=user,
                                   academicDiscipline=academic_discipline, location="",
                                   verifyHash=new_hash)
        verification_mail(request, user)
        user.save()
        user_profile.save()

        # academic discipline (required user in db)
        # -> add user to group uni, fac whatever and his academic discipline
        if GroupProfile.objects.filter(name=academic_discipline).exists():
            group = GroupProfile.objects.get(name=academic_discipline)
            while True:
                group.member.add(user)
                if group.supergroup is None:
                    break
                else:
                    group = group.supergroup

        return HttpResponseRedirect(reverse("twittur:pleaseVerify"))

    return render(request, 'index_ftu.html', context)


# Page: "Profilseite"
def profile_view(request, user):
    """
    view to display specific users information
    :param request:
    :param user: username of user to be displayed
    :return: rendered HTML in template 'profile.html'
    """

    if not request.user.is_authenticated():             # check if user is logged in
        return HttpResponseRedirect(reverse("twittur:login"))  # if user is not logged in, redirect to FTU

    user = user.lower()
    # initialize data dictionary 'context' with relevant display information
    context = get_context(request, 'profile', user)

    # GET request "Alle anzeigen" for group or favorites
    if 'favorits' in request.GET or 'favorits' in request.POST:
        context['show_favs'] = True
    elif 'group' in request.GET or 'group' in request.POST:
        context['show_groups'] = True
        # group_sb_list = GroupProfile.objects.filter(Q(member__exact=request.user))
        context['show_group_list'] = GroupProfile.objects.filter(Q(member__exact=request.user))

    if User.objects.filter(username=user).exists():
        p_user = User.objects.get(username=user)  # this is the user displayed in html
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
                context['success_msg'] = 'Sie folgen ' + user.upper() + ' jetzt nicht mehr.'
            else:
                note = request.user.username + ' folgt Dir jetzt!'
                set_notification('follower', data={'user': p_user, 'follower': context['userProfile'], 'note': note})
                context['success_msg'] = 'Sie folgen ' + user.upper() + ' jetzt.'

        elif 'entfollow' in data_dict:
            entfollow = User.objects.get(id=data_dict['entfollow'])
            follow = Notification.objects.get(Q(user__exact=entfollow) & Q(follower__exact=context['userProfile']))
            follow.delete()
            context['success_msg'] = entfollow.username + " wird nicht mehr gefolgt."

        elif 'leaveGroup' in data_dict:
            group = GroupProfile.objects.get(id=data_dict['leaveGroup'])
            group.member.remove(request.user)
            note = request.user.username + ' hat Ihre Gruppe verlassen.'
            set_notification('group', data={'group': group, 'member': group.admin, 'note': note})
            context['success_msg'] = 'Sie haben die Gruppe "' + group.name + '" verlassen.'

        context['follow_list'] = context['userProfile'].follow.all()

        if context['userProfile'].ignoreU.filter(username=p_user.username).exists():
            context['ignored'] = True                                   # yes, so disable all messages from her profile

        if p_user in context['follow_list']:
            context['follow_text'] = '<span class="glyphicon glyphicon-star-empty"></span> NICHT FOLGEN'
        else:
            context['follow_text'] = '<span class="glyphicon glyphicon-star"></span> FOLGEN'

        # Messages
        messages = get_messages(data={'page': 'profile', 'data': p_user, 'end': 5, 'request': request})

        context['list_length'], context['list_end'] = messages['list_length'], messages['list_end']
        context['has_msg'], context['message_list'] = messages['has_msg'], messages['message_list']

        if 'delMessage' or 'ignoreMsg' not in request.POST:
            context['list_end'] = messages['list_end']
    else:
        context = get_context(request, '404', user=request.user)
        context['error_type'] = 'ObjectDoesNotExist'
        context['error_site'] = 'Profilseite'
        context['error_object'] = user

        return render(request, 'error_404.html', context)
        # context['error_msg']['error_no_user'] = 'Kein Benutzer mit dem Benutzernamen ' + user + ' gefunden!'

    context['follow_sb_list'] = get_context(request, 'profile', user)['follow_sb_list']

    return render(request, 'profile.html', context)


# Page: "Einstellungen"
def profile_settings_view(request):
    """
    view to update account and personal information
    -- picture, email, password, first_name, last_name,
       academicDiscipline, location
    user can also delete its account
    :param request:
    :return: rendered HTML in template 'settings.html'
    """

    if not request.user.is_authenticated():             # check if user is logged in
        return HttpResponseRedirect(reverse("twittur:login"))  # if user is not logged in, redirect to FTU

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
            return HttpResponseRedirect(reverse("twittur:index"))
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
                        username = user.username
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
            if GroupProfile.objects.filter(name=user_profile.academicDiscipline).exists():
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

    # update current users information if changed
    if request.method == 'POST':
        user = User.objects.get(pk=request.user.id)
        user_profile = user.userprofile
        context['user'], context['userProfile'] = user, user_profile

    # initialize UserForm and UserDataForm with current users information
    context['userForm'], context['userDataForm'] = UserForm(instance=user), UserDataForm(instance=user_profile)
    context['discList'], context['safetyLevelList'] = get_disciplines(), get_safety_levels(user)

    return render(request, 'profile_settings.html', context)


# Page: "Nachricht / Konversation"
def message_view(request, msg):
    """
    view to show messages / conversations
    :param request:
    :param msg: ID of displayed message
    :return: rendered HTML in template 'message.html'
    """

    if not request.user.is_authenticated():             # check if user is logged in
        return HttpResponseRedirect(reverse("twittur:login"))  # if user is not logged in, redirect to FTU

    # initialize data dictionary 'context' with relevant display information
    context = get_context(request, page='message', user=request.user)
    context['msg_id'] = msg

    # if a message was sent to this view:
    # return success_msg
    if request.method == 'POST':
        context['success_msg'] = 'Nachricht erfolgreich gesendet!'

    # gets all Messages
    messages = get_messages(data={'page': msg, 'data': request.user, 'request': request})
    if not messages['message_list']:
        context = get_context(request, '404', user=request.user)
        context['error_type'] = 'ObjectDoesNotExist'
        context['error_site'] = 'Nachrichtenanzeige'
        context['error_object'] = msg
        return render(request, 'error_404.html', context)
    else:
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
        return HttpResponseRedirect(reverse("twittur:login"))  # if user is not logged in, redirect to FTU

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
        return HttpResponseRedirect(reverse("twittur:login"))  # if user is not logged in, redirect to FTU

    # initialize data dictionary 'context' with relevant display information
    context = get_context(request, '404', user=request.user)

    return render(request, 'error_404.html', context)


def please_verify_view(request):
    return render(request, 'index_please_verify.html', {'active_page': 'pleaseVerify'})


# Page: "NoScript-Fehler"
def no_script(request):
    """

    :param request:
    :return:
    """

    if not request.user.is_authenticated():             # check if user is logged in
        return HttpResponseRedirect(reverse("twittur:login"))  # if user is not logged in, redirect to FTU

    # initialize data dictionary 'context' with relevant display information
    context = get_context(request, 'noscript', user=request.user)

    return render(request, 'error_no_script.html', context)
