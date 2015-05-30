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
from .models import UserProfile, Group, Nav, Message




# startpage
def index(request):


	# redirect, if user is not authenticated 
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/twittur/login/')


	#print(request.user)
	current_user = User.objects.all().filter(username__exact=request.user.username).select_related('userprofile')
	user_list = UserProfile.objects.all().filter(userprofile__exact=request.user)
	atTag = '@' + request.user.username + ' '
	#print (atTag)
	message_list = Message.objects.all().select_related('user__userprofile').filter( Q(user__exact=request.user) | Q(text__contains=atTag))
	#print(message_list)
	messageList = Message.objects.all()
	#print(messageList)

	#user_list = User.objects.all()
	#message_list = Message.objects.all()
	#message_list = Message.objects.all().select_related('user')
	group_list = Group.objects.all()

	context = { 'active_page' : 'index', 'current_user' : current_user, 'user_list': user_list , 'message_list' : message_list , 'nav': Nav.nav }
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
			context = { 'active_page' : 'index', 'nav': Nav.nav }

			if user is not None:
				if user.is_active:
					auth.login(request, user)
					return HttpResponseRedirect('/twittur/')
			elif username=="" and password=="" :
				error_text = "Geben sie bitte Username und Passwort ein."
				return render(request, 'ftu.html', { 'error_text' : error_text } )	
			else:
				error_text = "Ups, Username oder Passwort falsch."
				active_toggle = "active_toggle"
				return render(request, 'ftu.html', { 'error_text' : error_text } )		

	# Registration
	if request.method == 'POST':

		# check if available
		try:
			query_dict = request.POST
			print(query_dict)
			username = query_dict.get('name')
			checkUsername = User.objects.get( username__exact = username )

		# case if username is available (checkUsername = None)
		except ObjectDoesNotExist:
			password = query_dict.get('password')
			ack_password = query_dict.get('ack_password')

			# check passwort and ack_password
			if password != ack_password :
				error_password = "Passwörter sind nicht gleich."
				return render(request, 'ftu.html', { 'error_password': error_password })

			email = query_dict.get('email')
			user = User.objects.create_user( username, email, password )
			user_profil = UserProfile(userprofile=user, studentNumber=000000, academicDiscipline='Informatik')
			user_profil.save()
			user = authenticate(username = username, password = password)
			context = { 'active_page' : 'index', 'nav': Nav.nav , 'user' : user_profil }
			auth.login(request, user)
			return render(request, 'index.html', context)

		# case if username is taken (checkUsername == user)
		else:
			error_user = "Sorry, Username ist vergeben."
			return render(request, 'ftu.html', { 'error_user': error_user })

	# twitter/login/
	context = { 'active_page' : 'ftu', 'nav': Nav.nav}
	return render(request, 'ftu.html', context)
# logout
def logout(request):
	
	auth.logout(request)
	
	#return render(request, 'ftu.html')
	return HttpResponseRedirect('/twittur/')

# profilpage
def profile(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/twittur/login/')
	user_list = User.objects.all()
	group_list = Group.objects.all()
	context = { 'active_page' : 'profile', 'user_list': user_list , 'group_list': group_list, 'nav': Nav.nav}
	return render(request, 'profile.html', context)

# infopage
def info(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/twittur/login/')

	context = { 'active_page' : 'info', 'nav': Nav.nav}
	return render(request, 'info.html', context)

# settingspage
def settings(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/twittur/login/')

	context = { 'active_page' : 'settings', 'nav': Nav.nav}
	return render(request, 'settings.html', context)
