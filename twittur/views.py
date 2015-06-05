import datetime

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from PPSN.settings import MEDIA_ROOT, MEDIA_URL

from django.contrib.auth.models import User
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth import authenticate, login
from django.contrib import auth
from .models import UserProfile, Group, Nav, Message, Hashtag, Has, ToUser
from .forms import UserForm, UserDataForm, MessageForm

# startpage
def index(request):

	# redirect, if user is not authenticated
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/twittur/login/')

	success_msg = None

	if request.method == 'POST' and 'delMessage' in request.POST:
		curMsg = Message.objects.get(pk = request.POST['delMessage'])
		curMsg.delete()
		success_msg = 'Nachricht gel&ouml;scht!'

	#print(request.user)
	current_user = User.objects.all().filter(username__exact=request.user.username).select_related('userprofile')
	user_list = UserProfile.objects.all().filter(userprofile__exact=request.user)
	atTag = '@' + request.user.username + ' '
	#print (atTag)
	message_list = Message.objects.all().select_related('user__userprofile')\
		.filter( Q(user__exact=request.user) | Q(text__contains=atTag)).order_by('-date')

	#print(message_list)
	message_list = Message.objects.all().order_by('-date')

	group_list = Group.objects.all()

	context = { 'active_page' : 'index', 'current_user' : current_user, 'user_list': user_list,
				'message_list': message_list , 'nav': Nav.nav, 'msgForm': msgDialog(request),
				'success_msg': success_msg }
	return render(request, 'index.html', context)


# login/registration page
def login(request):

	if request.user.is_authenticated():
		return HttpResponseRedirect('/twittur/')

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
				return render(request, 'ftu.html', { 'error_login' : error_login } )

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


	context = { 'active_page' : 'ftu', 'nav': Nav.nav}
	return render(request, 'ftu.html', context)

# logout
def logout(request):
	auth.logout(request)
	return HttpResponseRedirect('/twittur/')

# profilpage
def profile(request, user):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/twittur/login/')

	curUser = User.objects.get(username = user)
	curUserProfile = curUser.userprofile
	success_msg = None

	if request.method == 'POST' and 'delMessage' in request.POST:
		curMsg = Message.objects.get(pk = request.POST['delMessage'])
		curMsg.delete()
		success_msg = 'Nachricht gel&ouml;scht!'

	user_list = User.objects.all()
	group_list = Group.objects.all()
	
	message_list = Message.objects.all().select_related('user__userprofile')\
		.filter(
			Q(user__exact=request.user) | Q(text__contains='@' + request.user.username + ' ')
		).order_by('-date')
	
	context = { 'curUser': curUser, 
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

	projektTeam = User.objects.filter();

	context = {
		'active_page' : 'info',
		'nav': Nav.nav,
		'msgForm': msgDialog(request)
	}
	return render(request, 'info.html', context)

# settingspage
def settings(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/twittur/login/')

	curUser = User.objects.get(pk = request.user.id)
	curUserProfile = curUser.userprofile
	success_msg, error_msg, userForm, userDataForm = None, None, None, None

	if request.method == 'POST' and request.POST['delete'] == 'true':
		curUser.userprofile.delete()
		curUser.delete()
		return HttpResponseRedirect('/twittur/')
	elif request.method == 'POST':
		userForm = UserForm(request.POST, instance = curUser)
		if userForm.is_valid():
			userDataForm = UserDataForm(request.POST, request.FILES, instance = curUserProfile)
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

	userForm = UserForm(instance = curUser)
	userDataForm = UserDataForm(instance = curUserProfile)

	context = {
		'active_page' : 'settings',
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
	curUser = User.objects.get(pk = request.user.id)

	if request.method == 'POST':
		msgForm = MessageForm(request.POST)
		if msgForm.is_valid():
			
			text = msgForm.instance.text 

			
			print(text)
			# exstract # and @
			list_hashtag = []
			list_attag = []
			code = ""
			# boolean for # and @
			hashtag = False
			attag = False

			for i in text:

				# hashtag found
			    if i == "#" :
			        hashtag = True
			        print ("hashtag found")
			    # end with " "
			    if hashtag and i == " ":
			        list_hashtag.append(code)
			        code = ""
			        hashtag = False

			    if (hashtag):
			        code += i

			    # @ found
			    if i == "@" :
			        attag = True
			        print ("attag found")
			    # end with " "
			    if attag and i == " ":
			        list_attag.append(code)
			        code = ""
			        attag = False

			    if (attag):
			        code += i


			# Merge lists 
			list_link = list_hashtag + list_attag
			for element in list_link:
				msgForm.instance.text = msgForm.instance.text.replace(element,('<a href="">'+ element +'</a>'))
			print(msgForm.instance.text)
			msgForm.save()
			message = msgForm.instance
			# Check list with # 
			if list_hashtag:
				for ele in list_hashtag:
					# create hashtag table ele
					hashtag = Hashtag(name = ele)
					hashtag.save()
					has = Has(message=message, hashtag=hashtag)
					has.save()
					print (ele)

			# Check list with @
			if list_attag:
				for ele in list_attag:
					# username[0] = '' and username[1] = username
					username = ele.split('@')
					print(username[1])
					try:
						# check if user exist
						user = User.objects.get( username__exact = username[1] )
					except ObjectDoesNotExist:
						# there is no user with username
						pass
					else:
						# create ToUser ele
						touser = ToUser(toUser = user, message = message)
						touser.save()
						print (ele)


					
				
	msgForm = MessageForm(initial = {'user': curUser.id, 'date': datetime.datetime.now()})

	return msgForm

def search(request):

	if request.method == 'GET':
		query_dict = request.GET
		search = query_dict.get('search')

	message_list = Message.objects.all().select_related('user__userprofile')\
		.filter(
			  Q(text__contains=search) | Q(user__username__contains=search)
		).order_by('-date')

	context = {
		'search': search,
		'message_list': message_list,
		'active_page' : 'settings',
		'nav': Nav.nav,
	}
	return render(request, 'search.html', context)

def searchhashtag(request, text):
	search = text
	message_list = Message.objects.all().select_related('user__userprofile')\
		.filter(
			  Q(text__contains=text)
		).order_by('-date')
	print(text)
	context = {
		'search': search,
		'message_list': message_list,
		'active_page' : 'settings',
		'nav': Nav.nav,
	}
	return render(request, 'search.html', context)