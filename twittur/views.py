import copy, datetime, string, random, re

from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from .models import UserProfile, Nav, Message, Hashtag, GroupProfile
from .forms import UserForm, UserDataForm, GroupProfileForm
from .functions import dbm_to_m, editMessage, msgDialog


# startpage
def index(request):
    # check if user is logged in
    # if user is not logged in, redirect to FTU
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    has_msg, success_msg = None, None

    current_user = User.objects.filter(username__exact=request.user.username).select_related('userprofile')
    curUser = User.objects.get(username__exact=request.user)
    follow_list = curUser.userprofile.follow.all()
    hot_list = Hashtag.objects.annotate(hashtag_count=Count('hashtags__hashtags__name')) \
                   .order_by('-hashtag_count')[:5]
    user_list = UserProfile.objects.filter(userprofile__exact=request.user)
    #    atTag = '@' + request.user.username + ' '

    msgForm = msgDialog(request)
    if request.method == 'POST':
        success_msg = editMessage(request)

    # dbmessage_list = Message.objects.all().select_related('user__userprofile') \
    #        .filter(Q(user__exact=request.user) | Q(text__contains=atTag)).order_by('-date')
    dbmessage_list = Message.objects.all().filter(Q(user__exact=current_user)
                                                  | Q(user__exact=curUser.userprofile.follow.all())).order_by('-date')

    curDate = timezone.make_aware(datetime.datetime.now() - datetime.timedelta(minutes=10),
                                  timezone.get_current_timezone())

    # Group
    group_list = GroupProfile.objects.all().filter(Q(member__exact=request.user))


    message_list = []
    for message in dbmessage_list:
        if message.date > curDate:
            message.editable = True
        copy_message = copy.copy(message)
        message_list.append(dbm_to_m(copy_message))

    if len(message_list) > 0:
        has_msg = True
    message_list = zip(message_list, dbmessage_list)

    context = {'active_page': 'index', 'current_user': current_user, 'user_list': user_list,
               'message_list': message_list, 'nav': Nav.nav, 'msgForm': msgForm,'group_list': group_list,
               'success_msg': success_msg, 'has_msg': has_msg, 'hot_list': hot_list, 'follow_list': follow_list}
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
                    success_msg = 'Dein neues Passwort hast Du per E-Mail erhalten!'
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

    has_msg, error_msg, success_msg = None, {}, None
    # this is the login user
    cuUser = UserProfile.objects.get(userprofile=request.user)
    follow_list = cuUser.follow.all()

    # Group
    group_list = GroupProfile.objects.all().filter(Q(member__exact=request.user))

    try:
        curUser = User.objects.get(username=user)  # this is the user displayed in html
        curUserProfile = curUser.userprofile

        # follow
        if request.method == "GET" and 'follow' in request.GET:
            print(cuUser.follow.all())
            if curUser in cuUser.follow.all():
                print("remove")
                cuUser.follow.remove(curUser)
                cuUser.save()
            else:
                print("add")
                cuUser.follow.add(curUser)
                cuUser.save()

        if curUser in follow_list:
            follow_text = '<span class="glyphicon glyphicon-eye-close"></span> ' + user.upper() + ' nicht folgen'
        else:
            follow_text = '<span class="glyphicon glyphicon-eye-open"></span> ' + user.upper() + ' folgen'

        if request.method == 'POST':
            success_msg = editMessage(request)


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
        if len(message_list) > 0:
            has_msg = True
        message_list = zip(message_list, dbmessage_list)

        context = {'follow_list': follow_list,
                   'follow_text': follow_text,
                   'curUser': curUser,
                   'curUserProfile': curUserProfile,
                   'active_page': 'profile',
                   'profileUser': user,
                   'nav': Nav.nav,
                   'message_list': message_list,
                   'msgForm': msgDialog(request),
                   'has_msg': has_msg,
                   'success_msg': success_msg,
                   'group_list': group_list
                   }
    except:
        error_msg['error_no_user'] = 'Kein Benutzer mit dem Benutzernamen ' + user + ' gefunden!'
        context = {
            'active_page': 'profile',
            'nav': Nav.nav,
            'curUser': None,
            'error_msg': error_msg,
            'follow_list': follow_list,
            'group_list': group_list,
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
        'msgForm': msgDialog(request),
        'success_msg': success_msg,
        'error_msg': error_msg,
        'user': curUser,
        'userForm': userForm,
        'userDataForm': userDataForm
    }
    return render(request, 'settings.html', context)


'''
def follow(request, user):

    if request.method == 'GET':
        print("hello")
        print(request)

    profile(request, user)
    return HttpResponseRedirect('')
    '''

def pw_generator(size=6, chars=string.ascii_uppercase + string.digits): # found on http://goo.gl/RH995X
    return ''.join(random.choice(chars) for _ in range(size))

def addgroup(request):

    error = None
    if request.POST:
        groupProfileForm = GroupProfileForm(request.POST)
        print(groupProfileForm.is_valid())
        if groupProfileForm.is_valid():
            try:
                group = GroupProfile.objects.get(name__exact=groupProfileForm.instance.name)
            except ObjectDoesNotExist:
                groupProfileForm.instance.groupprofile = groupProfileForm.instance
                groupProfileForm.instance.admin = request.user
                groupProfileForm.save()
                groupProfileForm.instance.member.add(request.user)

                return HttpResponseRedirect('/twittur/group/' + groupProfileForm.instance.name)
            else:
                error = "Gruppenname ist schon vergeben, bitch!"

    groupProfileForm = GroupProfileForm()
    context = {
        'error': error,
        'groupProfileForm': groupProfileForm,
        'nav': Nav.nav,

    }

    return render(request, 'addgroup.html', context)

def group(request, groupname):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    group = GroupProfile.objects.get(name__exact=groupname)
    curUser = request.user
    context = {
        'group': group,
        'curUser': curUser,
        'nav': Nav.nav,
    }
    return render(request, 'group.html', context)