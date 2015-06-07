import datetime

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from PPSN.settings import MEDIA_ROOT, MEDIA_URL

from django.contrib.auth.models import User
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth import authenticate
from django.contrib import auth
from .models import UserProfile, Group, Nav, Message, FAQ, Hashtag
from .forms import UserForm, UserDataForm, MessageForm, FAQForm





import unicodedata

# startpage
def index(request):
    # redirect, if user is not authenticated
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    success_msg = None

    if request.method == 'POST':
        if 'delMessage' in request.POST:
            curMsg = Message.objects.get(pk=request.POST['delMessage'])
            curMsg.delete()
            success_msg = 'Nachricht gel&ouml;scht!'
        else:
            success_msg = 'Nachricht erfolgreich gesendet!'

    # print(request.user)
    current_user = User.objects.all().filter(username__exact=request.user.username).select_related('userprofile')
    user_list = UserProfile.objects.all().filter(userprofile__exact=request.user)
    atTag = '@' + request.user.username + ' '
    # print (atTag)
    message_list = Message.objects.all().select_related('user__userprofile') \
        .filter(Q(user__exact=request.user) | Q(text__contains=atTag)).order_by('-date')

    # print(message_list)
    message_list = Message.objects.all().order_by('-date')

    group_list = Group.objects.all()

    context = {'active_page': 'index', 'current_user': current_user, 'user_list': user_list,
               'message_list': message_list, 'nav': Nav.nav, 'msgForm': msgDialog(request),
               'success_msg': success_msg}
    return render(request, 'index.html', context)


# login/registration page
def login(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect('/twittur/')
		
	active_page = "ftu"
		
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
				return render(request, 'ftu.html', { 'error_login' : error_login, 'message_list':message_list, 'active_page':active_page } )

	# Registration
	if request.method == 'POST':

		query_dict = request.POST
		error_reg_user, error_reg_userprofil, error_reg_user_n, error_reg_user_p, error_reg_userprofile_e,  \
		error_reg_userprofile_ad, error_reg_userprofile_nr = None, None, None, None, None, None, None
		studentNumber = 0

		try:
			username = query_dict.get('name')
			checkUsername = User.objects.get( username__exact = username )
			
		# case if username is available (checkUsername = None)
		except ObjectDoesNotExist:
			password = query_dict.get('password')
			ack_password = query_dict.get('ack_password')

			# Password validation
			if password != ack_password :
				error_reg_user_p = " - Passw&ouml;rter sind nicht gleich."
			if " " in password:
				error_reg_user_p = " - Keine Leerzeichen in Passwort erlaubt."

			# context for html
			context = { 'active_page' : 'index', 
						'nav': Nav.nav , 
						'error_reg_user': error_reg_user, 
						'error_reg_userprofile_e': error_reg_userprofile_e,
						'error_reg_user_n': error_reg_user_n,
						'error_reg_user_p': error_reg_user_p,
						'error_reg_userprofile_ad': error_reg_userprofile_ad,
						'error_reg_userprofile_nr': error_reg_userprofile_nr,
						'rActive': 'active'
					}
			# error? 
			if 	error_reg_userprofile_ad or error_reg_userprofile_nr or error_reg_user or error_reg_userprofil or error_reg_user_p or error_reg_userprofile_e:
				return render(request, 'ftu.html', context)

			# fill the rest for modal User and Userprofile
			email = query_dict.get('email')
			if len(query_dict.get('studentNumber')) > 0: # if input is empty, keep default (0)
				studentNumber = query_dict.get('studentNumber')
			academicDiscipline = query_dict.get('academicDiscipline')
			first_name = query_dict.get('first_name')
			last_name = query_dict.get('last_name')
			
			# create User and Userprofile 
			user = User.objects.create_user( username, email, password )
			user.first_name = first_name
			user.last_name = last_name
			user.save()
			user_profil = UserProfile(userprofile=user, studentNumber=studentNumber, academicDiscipline=academicDiscipline, location="Irgendwo")
			user_profil.save()

			# log user in and redirect to index page
			user = authenticate(username = username, password = password)
			auth.login(request, user)
			return render(request, 'index.html', context)

		# case if username is taken (checkUsername == user)
		else:
			error_reg_user_n = "Sorry, Username ist vergeben."
			return render(request, 'ftu.html', { 'error_reg_user_n': error_reg_user_n, 'rActive': 'active' })


	

	

	context = { 'active_page' : 'ftu', 'nav': Nav.nav, 'message_list' : message_list}
	return render(request, 'ftu.html', context)


# logout
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/twittur/')


# profilpage
def profile(request, user):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    curUser = User.objects.get(username=user)
    curUserProfile = curUser.userprofile
    success_msg = None

    print user

    if request.method == 'POST' and 'delMessage' in request.POST:
        curMsg = Message.objects.get(pk=request.POST['delMessage'])
        curMsg.delete()
        success_msg = 'Nachricht gel&ouml;scht!'

    user_list = User.objects.all()
    group_list = Group.objects.all()

    message_list = Message.objects.all().select_related('user__userprofile') \
        .filter(
        Q(user__exact=curUser) | Q(attags__username__exact=curUser.username)
    ).order_by('-date')

    context = {'curUser': curUser,
               'curUserProfile': curUserProfile,
               'active_page': 'profile',
               'profileUser': user,
               'user_list': user_list,
               'group_list': group_list,
               'nav': Nav.nav,
               'message_list': message_list,
               'msgForm': msgDialog(request),
               'success_msg': success_msg
               }
    return render(request, 'profile.html', context)


# infopage
def info(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    projektTeam = User.objects.filter(is_superuser=True).order_by('last_name');

    context = {
        'active_page': 'info',
        'nav': Nav.nav,
        'msgForm': msgDialog(request),
        'team': projektTeam
    }
    return render(request, 'info.html', context)


# infopage
def faq(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    success_msg, error_msg = None, None

    if request.method == 'POST':
        faqForm = FAQForm(request.POST)
        if faqForm.is_valid():
            faqForm.save()
            success_msg = "Neuer FAQ Eintrag hinzugef&uuml;gt!"

    faqForm = FAQForm(instance=request.user)

    FAQs = FAQ.objects.all()
    faqMain = FAQ.objects.filter(category='Allgemeine Frage')
    faqStart = FAQ.objects.filter(category='Startseite')
    faqProfile = FAQ.objects.filter(category='Profilseite')
    faqInfo = FAQ.objects.filter(category='Infoseite')
    faqSettings = FAQ.objects.filter(category='Einstellungen')

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
        'success_msg': success_msg,
        'error_msg': error_msg
    }
    return render(request, 'info_faq.html', context)


# infopage
def support(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    context = {
        'active_page': 'info',
        'nav': Nav.nav,
        'msgForm': msgDialog(request)
    }
    return render(request, 'info_support.html', context)


# settingspage
def settings(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/twittur/login/')

    curUser = User.objects.get(pk=request.user.id)
    curUserProfile = curUser.userprofile
    success_msg, error_msg, userForm, userDataForm = None, None, None, None

    if request.method == 'POST' and request.POST['delete'] == 'true':
        curUser.userprofile.delete()
        curUser.delete()
        return HttpResponseRedirect('/twittur/')
    elif request.method == 'POST':
        userForm = UserForm(request.POST, instance=curUser)
        if userForm.is_valid():
            userDataForm = UserDataForm(request.POST, request.FILES, instance=curUserProfile)
            userDataForm.oldPicture = curUserProfile.picture
            if 'picture' in request.FILES or 'picture-clear' in request.POST:
                if userDataForm.oldPicture != 'picture/default.gif':
                    userDataForm.oldPicture.delete()
            if userDataForm.is_valid():
                userForm.save()
                userDataForm.save()
                success_msg = 'Benutzerdaten wurden erfolgreich aktualisiert.'
            else:
                error_msg = userDataForm.errors
        else:
            error_msg = userForm.errors

    userForm = UserForm(instance=curUser)
    userDataForm = UserDataForm(instance=curUserProfile)

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


def msgDialog(request):
    curUser = User.objects.get(pk=request.user.id)

    if request.method == 'POST':
        msgForm = MessageForm(request.POST)
        if msgForm.is_valid():
            text = msgForm.instance.text
            '''
            hashtags = [i for i in text.split() if i.startswith("#")]
            attags = [i for i in text.split() if i.startswith("@")]
            '''
            # for debug
            list = []

            # Step 1: replace all # and @ with link
            for word in text.split():
                if word[0] == "#":
                    list.append(word)
                    href = '<a href="/twittur/hashtag/' + word[1:] + '">' + word + '</a>'
                    print "# Step 1: " + word.encode("utf-8")
                    msgForm.instance.text = msgForm.instance.text.replace(word, href)
                if word[0] == "@":
                    try:
                        user = User.objects.get(username__exact=word[1:])
                    except ObjectDoesNotExist:
                        pass
                    else:
                        list.append(word)
                        href = '<a href="/twittur/profile/' + word[1:] + '">' + word + '</a>'
                        msgForm.instance.text = msgForm.instance.text.replace(word, href)
                        print "@ Step 1: " + word

            # save this shit for the next step
            print msgForm.instance.text
            print type(msgForm.instance.text)
            msgForm.save()

            # Step 2: add # and @ related with message in database
            for word in list:
                if word[0] == "#":
                    try:
                        hashtag = Hashtag.objects.get(name__exact=str(word))
                    except ObjectDoesNotExist:
                        hashtag = Hashtag(name=str(word))
                        hashtag.save()
                    msgForm.instance.hashtags.add(hashtag)
                    print "# Step 2: " + word
            # Check list with @
                if word[0] == "@":
                    user = User.objects.get(username__exact=str(word[1:]))
                    msgForm.instance.attags.add(user)
                    print "@ Step 2: " + word
            msgForm.save()
            print msgForm.instance.attags.all()
            print msgForm.instance.hashtags.all()

    msgForm = MessageForm(initial={'user': curUser.id, 'date': datetime.datetime.now()})
    return msgForm


def search(request):
    if request.method == 'GET':
        query_dict = request.GET
        search = query_dict.get('search')

    message_list = Message.objects.all().select_related('user__userprofile') \
        .filter(
        Q(text__contains=search) | Q(user__username__contains=search)
    ).order_by('-date')

    context = {
        'search': search,
        'message_list': message_list,
        'active_page': 'settings',
        'nav': Nav.nav,
        'msgForm': msgDialog(request),
    }
    return render(request, 'search.html', context)


def hashtag(request, text):
    search = "#" + text
    message_list = Message.objects.all().filter(hashtags__name=search)
    print(message_list)
    context = {

        'search': search,
        'message_list': message_list,
        'active_page': 'settings',
        'nav': Nav.nav,
        'msgForm': msgDialog(request),
    }
    return render(request, 'search.html', context)
