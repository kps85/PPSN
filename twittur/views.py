import copy, datetime
from datetime import date

from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from PPSN.settings import MEDIA_ROOT, MEDIA_URL
from .models import UserProfile, Group, Nav, Message, FAQ, Hashtag
from .forms import UserForm, UserDataForm, MessageForm, FAQForm


# startpage
def index(request):
    # check if user is logged in
    # if user is not logged in, redirect to FTU
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    success_msg = None

<<<<<<< HEAD
=======
    if request.method == 'POST':
        if 'delMessage' in request.POST:
            curMsg = Message.objects.get(pk=request.POST['delMessage'])
            curMsg.delete()
            success_msg = 'Nachricht gel&ouml;scht!'
        elif 'updateMsg' in request.POST:
            curMsg = Message.objects.get(pk=request.POST['updateMsg'])
            curMsg.text = request.POST['updatedText']
            msg_to_db(curMsg)
            curMsg.save()
            success_msg = 'Nachricht erfolgreich aktualisiert!'
        else:
            success_msg = 'Nachricht erfolgreich gesendet!'


>>>>>>> origin/dev
    current_user = User.objects.all().filter(username__exact=request.user.username).select_related('userprofile')
    user_list = UserProfile.objects.all().filter(userprofile__exact=request.user)
    atTag = '@' + request.user.username + ' '

    if request.method == 'POST':
        success_msg = editMessage(request)

    #dbmessage_list = Message.objects.all().select_related('user__userprofile') \
    #    .filter(Q(user__exact=request.user) | Q(text__contains=atTag)).order_by('-date')
    dbmessage_list = Message.objects.all().select_related('user__userprofile').order_by('-date')

    hashtag_list = Hashtag.objects.annotate(hashtag_count=Count('hashtags__hashtags__name')).order_by('-hashtag_count')[:5]

    curDate = timezone.make_aware(datetime.datetime.now() - datetime.timedelta(minutes=10), timezone.get_current_timezone());
    message_list = []
    for message in dbmessage_list:
        if message.date > curDate:
            message.editable = True
        copy_message = copy.copy(message)
        message_list.append(dbm_to_m(copy_message))
    message_list = zip(message_list, dbmessage_list)


    context = {'active_page': 'index', 'current_user': current_user, 'user_list': user_list,
               'message_list': message_list, 'nav': Nav.nav, 'msgForm': msgDialog(request),
               'success_msg': success_msg, 'hashtag_list': hashtag_list }
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
                              {'error_login': error_login, 'message_list': message_list, 'active_page': active_page})

    # Registration
    if request.method == 'POST':

        query_dict = request.POST
        error_reg_user, error_reg_userprofil, error_reg_user_n, error_reg_user_p, error_reg_userprofile_e, \
        error_reg_userprofile_ad, error_reg_userprofile_nr, error_reg_mail = None, None, None, None, None, None, None, None
        studentNumber = 0

        try:
            username = query_dict.get('name')
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
            return render(request, 'ftu.html', {'active_page': 'ftu', 'nav': Nav.nav, 'error_reg_user_n': error_reg_user_n, 'error_reg_mail': error_reg_mail, 'rActive': 'active'})

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
                                  timezone.get_current_timezone());
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


# Page: 'Info'
# - shows: Impressum, Projekt-Team, Projekt (Aufgabenstellung, Ziel)
# - template: info.html
def info(request):
    # check if user is logged in
    # if user is not logged in, redirect to FTU
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    # select admin users as Projekt-Team
    projektTeam = User.objects.filter(is_superuser=True).order_by('last_name');

    # return relevant information to render info.html
    context = {
        'active_page': 'info',
        'nav': Nav.nav,
        'msgForm': msgDialog(request),
        'team': projektTeam
    }
    return render(request, 'info.html', context)


# Page: 'FAQ'
# - shows: frequently asked questions
# - allows: adding and deleting FAQ entries
# - template: info_faq.html
def faq(request):
    # check if user is logged in
    # if user is not logged in, redirect to FTU
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    # initialize return information
    success_msg, error_msg = None, None

    # adding a FAQ entry
    # form: FAQform from forms.py
    if request.method == 'POST':
        faqForm = FAQForm(request.POST)
        if faqForm.is_valid():
            faqForm.save()
            success_msg = "Neuer FAQ Eintrag hinzugef&uuml;gt!"

    # initialize FAQForm with current user as respondent
    faqForm = FAQForm(instance=request.user)

    # initialize FAQ list for each category
    faqMain = FAQ.objects.filter(category='Allgemeine Frage')
    faqStart = FAQ.objects.filter(category='Startseite')
    faqProfile = FAQ.objects.filter(category='Profilseite')
    faqInfo = FAQ.objects.filter(category='Infoseite')
    faqSettings = FAQ.objects.filter(category='Einstellungen')

    # sum FAQs into one list
    FAQs = [faqMain, faqStart, faqProfile, faqInfo, faqSettings]

    # return relevant information to render info_faq.html
    context = {
        'active_page': 'info',
        'nav': Nav.nav,
        'msgForm': msgDialog(request),
        'faqForm': faqForm,
        'faqMain': faqMain,
        'faqStart': faqStart,
        'faqProfile': faqProfile,
        'faqInfo': faqInfo,
        'faqSettings': faqSettings,
        'FAQs': FAQs,
        'success_msg': success_msg,
        'error_msg': error_msg
    }
    return render(request, 'info_faq.html', context)


# Page: 'Support'
# - allows: submitting diverse requests TODO: implement data processing
# - template: info_support.html
def support(request):
    # check if user is logged in
    # if user is not logged in, redirect to FTU
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    # return relevant information to render info_faq.html
    context = {
        'active_page': 'info',
        'nav': Nav.nav,
        'msgForm': msgDialog(request)
    }
    return render(request, 'info_support.html', context)


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


# messagebox clicked on pencil button
def msgDialog(request):
    curUser = User.objects.get(pk=request.user.id)

    if request.method == 'POST':
        msgForm = MessageForm(request.POST)
        if msgForm.is_valid():
            msgForm.save()
            msg_to_db(msgForm.instance)
            msgForm.save()
            '''
            text = msgForm.instance.text
            # for debug
            hashtaglist = []
            attaglist = []

            # Step 1: replace all # and @ with link
            for word in text.split():
                # find all words starts with "#". No "/" allowed in hashtag.
                if word[0] == "#":
                    if "/" in word:
                        pass
                    else:
                        try:
                            hashtag = Hashtag.objects.get(name__exact=str(word[1:]))
                        except ObjectDoesNotExist:
                            hashtag = Hashtag(name=str(word[1:]))
                            hashtag.save()

                        msgForm.instance.hashtags.add(hashtag)
                        hashtaglist.append(hashtag)
                # now find in text all words start with "@". Its important to find this user in database.
                if word[0] == "@":
                    try:
                        user = User.objects.get(username__exact=str(word[1:]))
                    except ObjectDoesNotExist:
                        pass
                    else:
                        msgForm.instance.attags.add(user)
                        attaglist.append(user)
            print(hashtaglist)
            print(attaglist)
            print(msgForm.instance.hashtags.all())
            print(msgForm.instance.attags.all())
            for dbhashtag in msgForm.instance.hashtags.all():
                if dbhashtag not in hashtaglist:
                    msgForm.instance.hashtags.remove(dbhashtag)
            for dbattag in msgForm.instance.attags.all():
                if dbattag not in attaglist:
                    msgForm.instance.attags.remove(dbattag)

            print(hashtaglist)
            print(attaglist)
            print(msgForm.instance.hashtags.all())
            print(msgForm.instance.attags.all())
            '''
            # save this shit for the next step


    msgForm = MessageForm(initial={'user': curUser.id, 'date': datetime.datetime.now()})
    return msgForm

# edit or update Message
def editMessage(request):
    curMsg = Message.objects.get(pk=request.POST['delMessage'])         # select Message

    if 'delMessage' in request.POST:                                    # if Message should be deleted
        curMsg.delete()                                                 # delete selected Message
        return 'Nachricht gel&ouml;scht!'                               # return info

    elif 'updateMsg' in request.POST:                                   # if Message should be updated
        curMsg.text = request.POST['updatedText']                       # set Message text
        curMsg.save()                                                   # save and update Message
        return 'Nachricht erfolgreich aktualisiert!'                    # return info

    else:                                                               # if Message should be posted
        return 'Nachricht erfolgreich gesendet!'                        # return info, cause post is in msgDialog()


# search input
def search(request):
    if request.method == 'GET':
        query_dict = request.GET
        search = query_dict.get('search')

    # filter all messages contain the word  or all users contain the word
    message_list = Message.objects.all().select_related('user__userprofile') \
        .filter(
        Q(text__contains=search) | Q(user__username__contains=search)
    ).order_by('-date').distinct('text')
    context = {
        'search': search,
        'message_list': message_list,
        'active_page': 'settings',
        'nav': Nav.nav,
        'msgForm': msgDialog(request),
    }
    return render(request, 'search.html', context)


# click on hashtaglinks will redirect to this function.
def hashtag(request, text):
    search = text

    # filter all messages contain #
    dbmessage_list = Message.objects.all().filter(hashtags__name=search)
    message_list = []
    for message in dbmessage_list:
        copy_message = copy.copy(message)
        message_list.append(dbm_to_m(copy_message))
    message_list = zip(message_list, dbmessage_list)

    context = {

        'search': "#" + search,
        'message_list': message_list,
        'active_page': 'settings',
        'nav': Nav.nav,
        'msgForm': msgDialog(request),
    }
    return render(request, 'search.html', context)

# Message to database, save hashtags and attags in text into database
# (2) edit: changed message may contains other hashtags and attags or hashtags and attags may removed
def msg_to_db(message):
    hashtaglist = []
    attaglist = []

    # Step 1: replace all # and @ with link
    for word in message.text.split():
        # find all words starts with "#". No "/" allowed in hashtag.
        if word[0] == "#":
            if "/" in word:
                pass
            else:
                # database will save hashtag instead of #hashtag
                try:
                    hashtag = Hashtag.objects.get(name__exact=str(word[1:]))
                except ObjectDoesNotExist:
                    hashtag = Hashtag(name=str(word[1:]))
                    hashtag.save()

                message.hashtags.add(hashtag)
                hashtaglist.append(hashtag)
        # now find in text all words start with "@". Its important to find this user in database.
        if word[0] == "@":
            # database will save user instead of @user
            try:
                user = User.objects.get(username__exact=str(word[1:]))
            except ObjectDoesNotExist:
                pass
            else:
                message.attags.add(user)
                attaglist.append(user)

    # (2) check for hashtags and attags in database (remove if no reference), only for edit
    for dbhashtag in message.hashtags.all():
        if dbhashtag not in hashtaglist:
            message.hashtags.remove(dbhashtag)
    for dbattag in message.attags.all():
        if dbattag not in attaglist:
            message.attags.remove(dbattag)

    return message


# Database message to message (in template), replace all hashtags and attags in message with links
def dbm_to_m(message):
    # get hashtags and attags (models.ManyToMany) in message from database
    hashtag_list = message.hashtags.all()
    attag_list = message.attags.all()

    # message contains hashtags or atttags
    if attag_list or hashtag_list:
        for word in message.text.split():
            # find all words starts with "#" and replace them with a link. No "/" allowed in hashtag.
            if word[0] == "#" and (Hashtag.objects.get(name=word[1:]) in hashtag_list):
                href = '<a href="/twittur/hashtag/' + word[1:] + '">' + word + '</a>'
                message.text = message.text.replace(word, href)
            # now find in text all words start with "@". Its important to find this user in database.
            # if this user doesnt exist -> no need to set a link
            # else we will set a link to his profile
            if word[0] == "@" and (User.objects.get(username=word[1:]) in attag_list):
                    href = '<a href="/twittur/profile/' + word[1:] + '">' + word + '</a>'
                    message.text = message.text.replace(word, href)
    return message